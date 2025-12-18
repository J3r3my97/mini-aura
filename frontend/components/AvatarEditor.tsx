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
      // Calculate center position
      const containerRect = containerRef.current.getBoundingClientRect();
      const centerX = containerRect.width / 2;
      const centerY = containerRect.height / 2;

      // Position avatar at center using transform
      // Since transformOrigin is at (100px, 100px), we translate to center the origin point
      const el = avatarRef.current;
      el.style.left = '0px';
      el.style.top = '0px';
      el.style.transform = `translate(${centerX}px, ${centerY}px) rotate(${transform.rotate}deg) scale(${transform.scaleX}, ${transform.scaleY})`;

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

    // Get avatar's transform from DOM
    const transformStr = avatarEl.style.transform;

    // Parse transform values (translate, rotate, scale)
    const translateMatch = transformStr.match(/translate\(([^,]+)px,\s*([^)]+)px\)/);
    const scaleMatch = transformStr.match(/scale\(([^,)]+)(?:,\s*([^)]+))?\)/);
    const rotateMatch = transformStr.match(/rotate\(([^)]+)deg\)/);

    const translateX = translateMatch ? parseFloat(translateMatch[1]) : 0;
    const translateY = translateMatch ? parseFloat(translateMatch[2]) : 0;
    const scaleX = scaleMatch ? parseFloat(scaleMatch[1]) : 1;
    const scaleY = scaleMatch && scaleMatch[2] ? parseFloat(scaleMatch[2]) : scaleX;
    const rotateDeg = rotateMatch ? parseFloat(rotateMatch[1]) : 0;

    // Apply transformations and draw avatar
    ctx.save();

    // Avatar center position (translate now positions the center directly)
    const avatarCenterX = translateX * scaleFactorX;
    const avatarCenterY = translateY * scaleFactorY;

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
    <div className="w-full">
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
              height: 'auto',
              transformOrigin: '100px 100px', // Center of 200px image
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
                // Let Moveable handle the full transform
                target.style.transform = transform;
              }}
              onResize={({ target, transform }) => {
                // Let Moveable handle the full transform (includes translate, rotate, scale)
                target.style.transform = transform;
              }}
              onRotate={({ target, transform }) => {
                // Let Moveable handle the full transform
                target.style.transform = transform;
              }}
            />
          )}
        </div>

        {/* Hidden canvas for compositing */}
        <canvas ref={canvasRef} className="hidden" />

      {/* Action Buttons */}
      <div className="flex gap-4 justify-center flex-wrap mt-8">
        <button onClick={onCancel} className="neu-button px-8 py-3 text-lg">
          Create Another
        </button>
        <button onClick={handleDownload} className="neu-button-accent px-8 py-3 text-lg">
          💾 Download
        </button>
      </div>
    </div>
  );
}
