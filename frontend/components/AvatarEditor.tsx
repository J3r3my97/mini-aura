'use client';

import { useState, useRef, useEffect } from 'react';
import Moveable from 'react-moveable';

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

  // Transform state
  const [transform, setTransform] = useState({
    translateX: 0,
    translateY: 0,
    scaleX: 0.3,
    scaleY: 0.3,
    rotate: 0,
  });

  useEffect(() => {
    if (avatarRef.current) {
      setTarget(avatarRef.current);
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
    if (!containerRect) return;

    const scaleFactorX = bgImg.width / containerRect.width;
    const scaleFactorY = bgImg.height / containerRect.height;

    // Apply transformations and draw avatar
    ctx.save();

    // Translate to avatar position (scaled to canvas size)
    const centerX = (containerRect.width / 2 + transform.translateX) * scaleFactorX;
    const centerY = (containerRect.height / 2 + transform.translateY) * scaleFactorY;

    ctx.translate(centerX, centerY);
    ctx.rotate((transform.rotate * Math.PI) / 180);
    ctx.scale(transform.scaleX, transform.scaleY);

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
              top: '50%',
              left: '50%',
              width: '200px',
              transformOrigin: 'center center',
              transform: `translate(-50%, -50%) translate(${transform.translateX}px, ${transform.translateY}px) rotate(${transform.rotate}deg) scale(${transform.scaleX}, ${transform.scaleY})`,
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
              onDrag={({ translate }) => {
                setTransform((prev) => ({
                  ...prev,
                  translateX: translate[0],
                  translateY: translate[1],
                }));
              }}
              onResize={({ width, height, drag }) => {
                const scaleX = width / 200;
                const scaleY = height / 200;
                setTransform((prev) => ({
                  ...prev,
                  scaleX,
                  scaleY,
                  translateX: drag.translate[0],
                  translateY: drag.translate[1],
                }));
              }}
              onRotate={({ rotate, drag }) => {
                setTransform((prev) => ({
                  ...prev,
                  rotate,
                  translateX: drag.translate[0],
                  translateY: drag.translate[1],
                }));
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
