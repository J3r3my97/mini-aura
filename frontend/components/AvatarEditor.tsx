'use client';

import { useState, useRef, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import for client-side only library
const Moveable = dynamic(() => import('react-moveable'), {
  ssr: false,
  loading: () => null,
});

interface AvatarEditorProps {
  originalImageUrl: string;
  avatarImageUrl: string;
  onSave: (compositeBlob: Blob) => void;
  onCancel: () => void;
}

export default function AvatarEditor({
  originalImageUrl,
  avatarImageUrl,
  onSave,
  onCancel,
}: AvatarEditorProps) {
  const [target, setTarget] = useState<HTMLElement | null>(null);
  const avatarRef = useRef<HTMLImageElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Transform state (only for canvas rendering, not for live display)
  const [transform, setTransform] = useState({
    translateX: 0,
    translateY: 0,
    scaleX: 0.3,
    scaleY: 0.3,
    rotate: 0,
  });

  useEffect(() => {
    if (avatarRef.current && containerRef.current) {
      // Calculate center position in pixels
      const containerRect = containerRef.current.getBoundingClientRect();
      const centerX = containerRect.width / 2 - 100; // 100 = half of 200px width
      const centerY = containerRect.height / 2 - 100;

      // Position avatar at center initially
      const el = avatarRef.current;
      el.style.left = `${centerX}px`;
      el.style.top = `${centerY}px`;
      el.style.transform = `rotate(${transform.rotate}deg) scale(${transform.scaleX}, ${transform.scaleY})`;

      setTarget(el);
    }
  }, []);

  const handleDownload = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Load images
    const bgImg = new Image();
    const fgImg = new Image();

    bgImg.crossOrigin = 'anonymous';
    fgImg.crossOrigin = 'anonymous';

    await new Promise<void>((resolve) => {
      let loaded = 0;
      const checkLoaded = () => {
        loaded++;
        if (loaded === 2) resolve();
      };

      bgImg.onload = checkLoaded;
      fgImg.onload = checkLoaded;
      bgImg.src = originalImageUrl;
      fgImg.src = avatarImageUrl;
    });

    // Set canvas size to match background image
    canvas.width = bgImg.width;
    canvas.height = bgImg.height;

    // Draw background
    ctx.drawImage(bgImg, 0, 0);

    // Calculate avatar position relative to canvas
    const containerRect = containerRef.current?.getBoundingClientRect();
    const avatarEl = avatarRef.current;
    if (!containerRect || !avatarEl) return;

    const scaleFactorX = bgImg.width / containerRect.width;
    const scaleFactorY = bgImg.height / containerRect.height;

    // Get avatar's actual position and transform from DOM
    const avatarLeft = parseFloat(avatarEl.style.left || '0');
    const avatarTop = parseFloat(avatarEl.style.top || '0');
    const transformStr = avatarEl.style.transform;

    // Parse transform values
    const scaleMatch = transformStr.match(/scale\(([^,)]+)(?:,\s*([^)]+))?\)/);
    const rotateMatch = transformStr.match(/rotate\(([^)]+)\)/);
    const scaleX = scaleMatch ? parseFloat(scaleMatch[1]) : 1;
    const scaleY = scaleMatch && scaleMatch[2] ? parseFloat(scaleMatch[2]) : scaleX;
    const rotateDeg = rotateMatch ? parseFloat(rotateMatch[1]) : 0;

    // Apply transformations and draw avatar
    ctx.save();

    // Avatar center position (avatar is 200px wide, positioned at top-left)
    const avatarCenterX = (avatarLeft + 100) * scaleFactorX; // 100 = half of 200px
    const avatarCenterY = (avatarTop + 100) * scaleFactorY;

    ctx.translate(avatarCenterX, avatarCenterY);
    ctx.rotate((rotateDeg * Math.PI) / 180);
    ctx.scale(scaleX, scaleY);

    // Draw avatar centered at current position
    ctx.drawImage(
      fgImg,
      -fgImg.width / 2,
      -fgImg.height / 2,
      fgImg.width,
      fgImg.height
    );

    ctx.restore();

    // Convert to blob and callback
    canvas.toBlob((blob) => {
      if (blob) {
        onSave(blob);
      }
    }, 'image/png');
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="neu-card rounded-3xl p-8 max-w-5xl w-full max-h-[95vh] overflow-auto shadow-2xl">
        <h2 className="text-4xl font-bold mb-3 text-center bg-gradient-to-br from-[#4a4a5e] to-[#8b7fc7] bg-clip-text text-transparent">
          Customize Your Avatar
        </h2>

        <div className="mb-8 text-center">
          <p className="text-[#7a7a8e] text-lg">
            🎯 <span className="font-semibold">Drag</span> to move •{' '}
            🔄 <span className="font-semibold">Corners</span> to resize •{' '}
            🔃 <span className="font-semibold">Handle</span> to rotate
          </p>
        </div>

        {/* Editor Container */}
        <div
          ref={containerRef}
          className="relative mx-auto mb-8 neu-card rounded-2xl overflow-hidden"
          style={{
            width: '100%',
            maxWidth: '600px',
            aspectRatio: '1',
          }}
        >
          {/* Background Image */}
          <img
            src={originalImageUrl}
            alt="Original"
            className="absolute inset-0 w-full h-full object-cover"
          />

          {/* Avatar Image (Moveable) */}
          <img
            ref={avatarRef}
            src={avatarImageUrl}
            alt="Avatar"
            className="absolute cursor-move"
            style={{
              width: '200px',
              transformOrigin: 'center center',
            }}
          />

          {/* Moveable Controls */}
          {target && (
            <Moveable
              target={target}
              draggable={true}
              resizable={true}
              rotatable={true}
              keepRatio={true}
              origin={false}
              onDrag={({ target, transform }) => {
                // Directly update DOM - no React re-render during drag
                target.style.transform = transform;
              }}
              onResize={({ target, transform }) => {
                // Directly update DOM - no React re-render during resize
                target.style.transform = transform;
              }}
              onRotate={({ target, transform }) => {
                // Directly update DOM - no React re-render during rotate
                target.style.transform = transform;
              }}
            />
          )}
        </div>

        {/* Hidden canvas for compositing */}
        <canvas ref={canvasRef} className="hidden" />

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center flex-wrap">
          <button onClick={onCancel} className="neu-button px-8 py-3 text-lg">
            Cancel
          </button>
          <button onClick={handleDownload} className="neu-button-accent px-8 py-3 text-lg">
            💾 Save & Download
          </button>
        </div>
      </div>
    </div>
  );
}
