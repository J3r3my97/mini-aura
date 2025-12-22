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

  // Transform state (synced with DOM for canvas rendering)
  const [transform, setTransform] = useState({
    translateX: 0,
    translateY: 0,
    scaleX: 0.3,
    scaleY: 0.3,
    rotate: 0,
  });

  // GBA button press states for visual feedback
  const [pressedKeys, setPressedKeys] = useState<Set<string>>(new Set());

  // Helper function to parse transform string and update state
  const syncTransformState = (transformStr: string) => {
    // Try to parse named transform functions first
    const translateMatch = transformStr.match(/translate\(([^,]+)px,\s*([^)]+)px\)/);
    const scaleMatch = transformStr.match(/scale\(([^,)]+)(?:,\s*([^)]+))?\)/);
    const rotateMatch = transformStr.match(/rotate\(([^)]+)deg\)/);

    if (translateMatch || scaleMatch || rotateMatch) {
      const x = translateMatch ? parseFloat(translateMatch[1]) : transform.translateX;
      const y = translateMatch ? parseFloat(translateMatch[2]) : transform.translateY;
      const scaleX = scaleMatch ? parseFloat(scaleMatch[1]) : transform.scaleX;
      const scaleY = scaleMatch && scaleMatch[2] ? parseFloat(scaleMatch[2]) : scaleX;
      const rotation = rotateMatch ? parseFloat(rotateMatch[1]) : transform.rotate;

      setTransform({
        translateX: x,
        translateY: y,
        scaleX,
        scaleY,
        rotate: rotation,
      });
    } else {
      // Fallback: Try to parse matrix transform
      const matrixMatch = transformStr.match(/matrix\(([^)]+)\)/);
      if (matrixMatch && avatarRef.current) {
        const values = matrixMatch[1].split(',').map(v => parseFloat(v.trim()));
        if (values.length === 6) {
          // matrix(a, b, c, d, e, f) where:
          // a, d = scale, b, c = rotation/skew, e, f = translate
          const [a, b, c, d, e, f] = values;
          const scaleX = Math.sqrt(a * a + b * b);
          const scaleY = Math.sqrt(c * c + d * d);
          const rotation = Math.atan2(b, a) * (180 / Math.PI);

          setTransform({
            translateX: e,
            translateY: f,
            scaleX,
            scaleY,
            rotate: rotation,
          });
        }
      }
    }
  };

  useEffect(() => {
    if (avatarRef.current && containerRef.current) {
      // Calculate center position
      const containerRect = containerRef.current.getBoundingClientRect();
      const centerX = containerRect.width / 2;
      const centerY = containerRect.height / 2;

      // Update transform state with center position
      const initialTransform = {
        translateX: centerX,
        translateY: centerY,
        scaleX: 0.3,
        scaleY: 0.3,
        rotate: 0,
      };
      setTransform(initialTransform);

      // Position avatar at center using transform
      const el = avatarRef.current;
      el.style.left = '0px';
      el.style.top = '0px';
      el.style.transform = `translate(${centerX}px, ${centerY}px) rotate(0deg) scale(0.3, 0.3)`;

      setTarget(el);
    }
  }, []);

  // GBA Controls - Keyboard event handlers
  useEffect(() => {
    const MOVE_STEP = 5; // pixels per key press
    const SCALE_STEP = 0.05; // scale increment
    const ROTATE_STEP = 5; // degrees per press

    const handleKeyDown = (e: KeyboardEvent) => {
      if (!avatarRef.current) return;

      const el = avatarRef.current;
      const currentTransform = el.style.transform;

      // Parse current values
      const translateMatch = currentTransform.match(/translate\(([^,]+)px,\s*([^)]+)px\)/);
      const scaleMatch = currentTransform.match(/scale\(([^,)]+)(?:,\s*([^)]+))?\)/);
      const rotateMatch = currentTransform.match(/rotate\(([^)]+)deg\)/);

      let x = translateMatch ? parseFloat(translateMatch[1]) : 0;
      let y = translateMatch ? parseFloat(translateMatch[2]) : 0;
      let scale = scaleMatch ? parseFloat(scaleMatch[1]) : 0.3;
      let rotation = rotateMatch ? parseFloat(rotateMatch[1]) : 0;

      let updated = false;

      // D-Pad - Arrow keys for movement
      if (e.key === 'ArrowUp') {
        y -= MOVE_STEP;
        updated = true;
        setPressedKeys(prev => new Set(prev).add('up'));
      } else if (e.key === 'ArrowDown') {
        y += MOVE_STEP;
        updated = true;
        setPressedKeys(prev => new Set(prev).add('down'));
      } else if (e.key === 'ArrowLeft') {
        x -= MOVE_STEP;
        updated = true;
        setPressedKeys(prev => new Set(prev).add('left'));
      } else if (e.key === 'ArrowRight') {
        x += MOVE_STEP;
        updated = true;
        setPressedKeys(prev => new Set(prev).add('right'));
      }
      // A Button - Size UP
      else if (e.key.toLowerCase() === 'a' || e.key === ' ') {
        scale = Math.min(scale + SCALE_STEP, 2); // Max 2x
        updated = true;
        setPressedKeys(prev => new Set(prev).add('a'));
        e.preventDefault();
      }
      // B Button - Size DOWN
      else if (e.key.toLowerCase() === 'b') {
        scale = Math.max(scale - SCALE_STEP, 0.1); // Min 0.1x
        updated = true;
        setPressedKeys(prev => new Set(prev).add('b'));
      }
      // L Shoulder - Rotate LEFT
      else if (e.key.toLowerCase() === 'q' || e.key.toLowerCase() === 'l') {
        rotation -= ROTATE_STEP;
        updated = true;
        setPressedKeys(prev => new Set(prev).add('l'));
      }
      // R Shoulder - Rotate RIGHT
      else if (e.key.toLowerCase() === 'e' || e.key.toLowerCase() === 'r') {
        rotation += ROTATE_STEP;
        updated = true;
        setPressedKeys(prev => new Set(prev).add('r'));
      }

      if (updated) {
        el.style.transform = `translate(${x}px, ${y}px) rotate(${rotation}deg) scale(${scale})`;
        // Update transform state for canvas rendering
        setTransform({
          translateX: x,
          translateY: y,
          scaleX: scale,
          scaleY: scale,
          rotate: rotation,
        });
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      // Clear pressed state on key up
      setPressedKeys(prev => {
        const next = new Set(prev);
        if (e.key === 'ArrowUp') next.delete('up');
        if (e.key === 'ArrowDown') next.delete('down');
        if (e.key === 'ArrowLeft') next.delete('left');
        if (e.key === 'ArrowRight') next.delete('right');
        if (e.key.toLowerCase() === 'a' || e.key === ' ') next.delete('a');
        if (e.key.toLowerCase() === 'b') next.delete('b');
        if (e.key.toLowerCase() === 'q' || e.key.toLowerCase() === 'l') next.delete('l');
        if (e.key.toLowerCase() === 'e' || e.key.toLowerCase() === 'r') next.delete('r');
        return next;
      });
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  const handleDownload = async () => {
    console.log('Starting download with transform:', transform);

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

    // Get container dimensions
    const containerRect = containerRef.current?.getBoundingClientRect();
    if (!containerRect) return;

    // Calculate how the background image is displayed with object-contain
    // object-contain scales to fit inside the container while maintaining aspect ratio
    const containerAspect = containerRect.width / containerRect.height;
    const imageAspect = bgImg.width / bgImg.height;

    let displayedBgWidth, displayedBgHeight, bgOffsetX, bgOffsetY;

    if (imageAspect > containerAspect) {
      // Image is wider - constrained by width
      displayedBgWidth = containerRect.width;
      displayedBgHeight = containerRect.width / imageAspect;
      bgOffsetX = 0;
      bgOffsetY = (containerRect.height - displayedBgHeight) / 2;
    } else {
      // Image is taller - constrained by height
      displayedBgWidth = containerRect.height * imageAspect;
      displayedBgHeight = containerRect.height;
      bgOffsetX = (containerRect.width - displayedBgWidth) / 2;
      bgOffsetY = 0;
    }

    // Set canvas size to match background image actual size
    canvas.width = bgImg.width;
    canvas.height = bgImg.height;

    // Draw background at full resolution
    ctx.drawImage(bgImg, 0, 0, bgImg.width, bgImg.height);

    // Scale factors to convert from screen coordinates to canvas coordinates
    const scaleFactor = bgImg.width / displayedBgWidth; // Same for X and Y since we maintain aspect ratio

    // Avatar is displayed at 200px width on screen
    const avatarDisplayWidth = 200;

    // Use transform state values for canvas rendering
    const { translateX, translateY, scaleX, scaleY, rotate: rotateDeg } = transform;

    console.log('Canvas rendering:', {
      containerSize: { width: containerRect.width, height: containerRect.height },
      displayedBgSize: { width: displayedBgWidth, height: displayedBgHeight },
      bgOffset: { x: bgOffsetX, y: bgOffsetY },
      canvasSize: { width: canvas.width, height: canvas.height },
      avatarImageSize: { width: fgImg.width, height: fgImg.height },
      avatarDisplayWidth,
      scaleFactor,
      transform: { translateX, translateY, scaleX, scaleY, rotateDeg }
    });

    // Apply transformations and draw avatar
    ctx.save();

    // Adjust for background image offset due to object-contain centering
    const adjustedX = translateX - bgOffsetX;
    const adjustedY = translateY - bgOffsetY;

    // Avatar center position in canvas coordinates
    const avatarCenterX = adjustedX * scaleFactor;
    const avatarCenterY = adjustedY * scaleFactor;

    ctx.translate(avatarCenterX, avatarCenterY);
    ctx.rotate((rotateDeg * Math.PI) / 180);
    ctx.scale(scaleX * scaleFactor, scaleY * scaleFactor);

    // Draw avatar at its display size
    const avatarDrawWidth = avatarDisplayWidth;
    const avatarDrawHeight = (fgImg.height / fgImg.width) * avatarDisplayWidth;

    ctx.drawImage(
      fgImg,
      -avatarDrawWidth / 2,
      -avatarDrawHeight / 2,
      avatarDrawWidth,
      avatarDrawHeight
    );

    ctx.restore();

    // Convert to blob and callback
    canvas.toBlob((blob) => {
      if (blob) {
        console.log('Canvas composited successfully. Blob size:', blob.size, 'bytes');
        onSave(blob);
      } else {
        console.error('Failed to create blob from canvas');
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
            className="absolute inset-0 w-full h-full object-contain"
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
                syncTransformState(transform);
              }}
              onResize={({ target, transform }) => {
                // Let Moveable handle the full transform (includes translate, rotate, scale)
                target.style.transform = transform;
                syncTransformState(transform);
              }}
              onRotate={({ target, transform }) => {
                // Let Moveable handle the full transform
                target.style.transform = transform;
                syncTransformState(transform);
              }}
            />
          )}
        </div>

        {/* Hidden canvas for compositing */}
        <canvas ref={canvasRef} className="hidden" />

      {/* GBA Controller UI */}
      <div className="mt-8 mx-auto max-w-2xl">
        <div className="neu-card rounded-3xl p-6 bg-gradient-to-br from-[#9b8bc9] to-[#7b6bb0] relative">
          {/* Shoulder Buttons (L/R) - Top */}
          <div className="absolute -top-4 left-0 right-0 flex justify-between px-8">
            <div className="flex flex-col items-center">
              <button
                className={`w-24 h-10 rounded-t-xl rounded-b-md font-bold text-lg transition-all ${
                  pressedKeys.has('l')
                    ? 'bg-[#4a4a5e] shadow-inner'
                    : 'bg-[#5a5a6e] shadow-lg hover:bg-[#4a4a5e]'
                }`}
                onMouseDown={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'q' }))}
                onMouseUp={() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'q' }))}
              >
                L
              </button>
              <div className="text-[#e6e7f0] text-xs mt-1 font-semibold">Q</div>
            </div>
            <div className="flex flex-col items-center">
              <button
                className={`w-24 h-10 rounded-t-xl rounded-b-md font-bold text-lg transition-all ${
                  pressedKeys.has('r')
                    ? 'bg-[#4a4a5e] shadow-inner'
                    : 'bg-[#5a5a6e] shadow-lg hover:bg-[#4a4a5e]'
                }`}
                onMouseDown={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'e' }))}
                onMouseUp={() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'e' }))}
              >
                R
              </button>
              <div className="text-[#e6e7f0] text-xs mt-1 font-semibold">E</div>
            </div>
          </div>

          {/* Main Controller Panel */}
          <div className="flex items-center justify-around gap-8 pt-6">
            {/* D-Pad */}
            <div className="flex flex-col items-center">
              <div className="text-[#e6e7f0] text-xs font-semibold mb-2">D-PAD</div>
              <div className="relative w-32 h-32">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="grid grid-cols-3 grid-rows-3 gap-1">
                    <div></div>
                    <button
                      className={`w-8 h-8 rounded-lg transition-all ${
                        pressedKeys.has('up')
                          ? 'bg-[#4a4a5e] shadow-inner'
                          : 'bg-[#2a2a3e] shadow-lg'
                      }`}
                      onMouseDown={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp' }))}
                      onMouseUp={() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowUp' }))}
                    >
                      ▲
                    </button>
                    <div></div>
                    <button
                      className={`w-8 h-8 rounded-lg transition-all ${
                        pressedKeys.has('left')
                          ? 'bg-[#4a4a5e] shadow-inner'
                          : 'bg-[#2a2a3e] shadow-lg'
                      }`}
                      onMouseDown={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }))}
                      onMouseUp={() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowLeft' }))}
                    >
                      ◄
                    </button>
                    <div className="w-8 h-8"></div>
                    <button
                      className={`w-8 h-8 rounded-lg transition-all ${
                        pressedKeys.has('right')
                          ? 'bg-[#4a4a5e] shadow-inner'
                          : 'bg-[#2a2a3e] shadow-lg'
                      }`}
                      onMouseDown={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }))}
                      onMouseUp={() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowRight' }))}
                    >
                      ►
                    </button>
                    <div></div>
                    <button
                      className={`w-8 h-8 rounded-lg transition-all ${
                        pressedKeys.has('down')
                          ? 'bg-[#4a4a5e] shadow-inner'
                          : 'bg-[#2a2a3e] shadow-lg'
                      }`}
                      onMouseDown={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown' }))}
                      onMouseUp={() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowDown' }))}
                    >
                      ▼
                    </button>
                    <div></div>
                  </div>
                </div>
              </div>
              <div className="text-[#e6e7f0]/60 text-xs mt-2">Arrow Keys</div>
            </div>

            {/* Center Info */}
            <div className="flex flex-col items-center justify-center">
              <div className="text-[#e6e7f0] text-lg font-bold mb-2">MOVE</div>
              <div className="text-[#e6e7f0]/60 text-sm">↑↓←→</div>
              <div className="h-4"></div>
              <div className="text-[#e6e7f0] text-lg font-bold mb-2">ROTATE</div>
              <div className="text-[#e6e7f0]/60 text-sm">L • R</div>
            </div>

            {/* Action Buttons (A/B) */}
            <div className="flex flex-col items-center">
              <div className="text-[#e6e7f0] text-xs font-semibold mb-2">SIZE</div>
              <div className="flex gap-4 items-center">
                <div className="flex flex-col items-center">
                  <button
                    className={`w-16 h-16 rounded-full font-bold text-2xl transition-all ${
                      pressedKeys.has('b')
                        ? 'bg-[#e74c3c] shadow-inner'
                        : 'bg-[#e67e73] shadow-lg hover:bg-[#e74c3c]'
                    }`}
                    onMouseDown={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'b' }))}
                    onMouseUp={() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'b' }))}
                  >
                    B
                  </button>
                  <div className="text-[#e6e7f0]/60 text-xs mt-1">Down</div>
                </div>
                <div className="flex flex-col items-center">
                  <button
                    className={`w-16 h-16 rounded-full font-bold text-2xl transition-all ${
                      pressedKeys.has('a')
                        ? 'bg-[#27ae60] shadow-inner'
                        : 'bg-[#52c89a] shadow-lg hover:bg-[#27ae60]'
                    }`}
                    onMouseDown={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'a' }))}
                    onMouseUp={() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'a' }))}
                  >
                    A
                  </button>
                  <div className="text-[#e6e7f0]/60 text-xs mt-1">Up</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-center flex-wrap mt-6">
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
