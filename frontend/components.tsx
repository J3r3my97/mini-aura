/**
 * Mini-Me Neumorphic Component Library
 * Reusable components following the Neumorphism design system
 */

import { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from 'react';

// ============================================================================
// BUTTON COMPONENTS
// ============================================================================

interface NeuButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'accent';
  children: ReactNode;
}

export function NeuButton({ variant = 'default', children, className = '', ...props }: NeuButtonProps) {
  const baseClasses = variant === 'accent' ? 'neu-button-accent' : 'neu-button';

  return (
    <button className={`${baseClasses} ${className}`} {...props}>
      {children}
    </button>
  );
}

// ============================================================================
// CARD COMPONENTS
// ============================================================================

interface NeuCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

export function NeuCard({ children, className = '', hover = true, onClick }: NeuCardProps) {
  return (
    <div
      className={`neu-card ${hover ? 'hover-enabled' : ''} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
}

// ============================================================================
// INPUT COMPONENTS
// ============================================================================

interface NeuInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function NeuInput({ label, error, className = '', ...props }: NeuInputProps) {
  return (
    <div className="w-full">
      {label && <label className="block text-sm font-semibold text-neu-text-primary mb-2">{label}</label>}
      <input className={`neu-input ${error ? 'border-2 border-red-400' : ''} ${className}`} {...props} />
      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
    </div>
  );
}

interface NeuTextareaProps extends InputHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  rows?: number;
}

export function NeuTextarea({ label, error, rows = 4, className = '', ...props }: NeuTextareaProps) {
  return (
    <div className="w-full">
      {label && <label className="block text-sm font-semibold text-neu-text-primary mb-2">{label}</label>}
      <textarea
        className={`neu-input resize-none ${error ? 'border-2 border-red-400' : ''} ${className}`}
        rows={rows}
        {...props as any}
      />
      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
    </div>
  );
}

// ============================================================================
// ICON WRAPPER
// ============================================================================

interface NeuIconProps {
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function NeuIcon({ children, size = 'md', className = '' }: NeuIconProps) {
  const sizeClasses = {
    sm: 'w-12 h-12',
    md: 'w-20 h-20',
    lg: 'w-28 h-28',
  };

  return (
    <div
      className={`${sizeClasses[size]} bg-neu-bg-primary rounded-full flex items-center justify-center ${className}`}
      style={{
        boxShadow: '8px 8px 16px #c8c9d4, -8px -8px 16px #ffffff',
      }}
    >
      {children}
    </div>
  );
}

// ============================================================================
// FEATURE CARD
// ============================================================================

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
}

export function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <NeuCard className="p-10 text-center rounded-3xl">
      <NeuIcon className="mx-auto mb-6">{icon}</NeuIcon>
      <h3 className="text-2xl font-bold mb-3 text-neu-text-primary">{title}</h3>
      <p className="text-neu-text-secondary">{description}</p>
    </NeuCard>
  );
}

// ============================================================================
// PRICING CARD
// ============================================================================

interface PricingCardProps {
  name: string;
  price: string;
  period: string;
  features: string[];
  featured?: boolean;
  badge?: string;
  onSelect?: () => void;
}

export function PricingCard({ name, price, period, features, featured = false, badge, onSelect }: PricingCardProps) {
  return (
    <NeuCard
      className={`p-12 text-center rounded-3xl ${
        featured ? 'bg-gradient-to-br from-[#8b7fc7]/10 to-[#6b5eb0]/10' : ''
      }`}
    >
      {badge && (
        <div className="inline-block bg-[#8b7fc7] text-white px-4 py-1.5 rounded-xl text-xs font-bold uppercase mb-4">
          {badge}
        </div>
      )}
      <h3 className="text-3xl font-extrabold mb-4 text-neu-text-primary">{name}</h3>
      <div className="mb-2">
        <span className="text-6xl font-extrabold text-[#8b7fc7]">{price}</span>
        <span className="text-xl text-neu-text-secondary font-medium">/{period}</span>
      </div>
      <ul className="space-y-3 my-8 text-left">
        {features.map((feature, idx) => (
          <li key={idx} className="flex items-center gap-3 text-neu-text-secondary">
            <span className="text-[#7bc89d] font-bold text-lg">✓</span>
            {feature}
          </li>
        ))}
      </ul>
      <NeuButton variant={featured ? 'accent' : 'default'} className="w-full" onClick={onSelect}>
        {featured ? 'Start Free Trial' : 'Get Started'}
      </NeuButton>
    </NeuCard>
  );
}

// ============================================================================
// TOGGLE / SWITCH
// ============================================================================

interface NeuToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
}

export function NeuToggle({ checked, onChange, label }: NeuToggleProps) {
  return (
    <label className="flex items-center gap-4 cursor-pointer">
      <div
        className={`relative w-16 h-8 rounded-full transition-all duration-300 ${
          checked ? 'bg-gradient-to-r from-[#8b7fc7] to-[#6b5eb0]' : 'bg-neu-bg-primary'
        }`}
        style={{
          boxShadow: checked
            ? 'inset 2px 2px 4px rgba(0,0,0,0.2)'
            : 'inset 4px 4px 8px #c8c9d4, inset -4px -4px 8px #ffffff',
        }}
        onClick={() => onChange(!checked)}
      >
        <div
          className={`absolute top-1 transition-all duration-300 w-6 h-6 rounded-full ${
            checked ? 'right-1 bg-white' : 'left-1 bg-white'
          }`}
          style={{
            boxShadow: '2px 2px 4px rgba(0,0,0,0.1)',
          }}
        />
      </div>
      {label && <span className="text-neu-text-primary font-medium">{label}</span>}
    </label>
  );
}

// ============================================================================
// LOADER / SPINNER
// ============================================================================

interface NeuLoaderProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export function NeuLoader({ size = 'md', text }: NeuLoaderProps) {
  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-16 h-16',
    lg: 'w-24 h-24',
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className={`loader ${sizeClasses[size]}`} />
      {text && <p className="text-neu-text-secondary">{text}</p>}
    </div>
  );
}

// ============================================================================
// BADGE
// ============================================================================

interface NeuBadgeProps {
  children: ReactNode;
  variant?: 'default' | 'accent' | 'success';
  className?: string;
}

export function NeuBadge({ children, variant = 'default', className = '' }: NeuBadgeProps) {
  const variantClasses = {
    default: 'bg-neu-bg-secondary text-neu-text-primary',
    accent: 'bg-gradient-to-r from-[#8b7fc7] to-[#6b5eb0] text-white',
    success: 'bg-[#7bc89d] text-white',
  };

  return (
    <span
      className={`inline-block px-4 py-1.5 rounded-xl text-xs font-bold uppercase ${variantClasses[variant]} ${className}`}
      style={{
        boxShadow: variant === 'default' ? '2px 2px 4px #c8c9d4, -2px -2px 4px #ffffff' : 'none',
      }}
    >
      {children}
    </span>
  );
}

// ============================================================================
// PROGRESS BAR
// ============================================================================

interface NeuProgressProps {
  value: number; // 0-100
  showLabel?: boolean;
  className?: string;
}

export function NeuProgress({ value, showLabel = true, className = '' }: NeuProgressProps) {
  const clampedValue = Math.min(Math.max(value, 0), 100);

  return (
    <div className={`w-full ${className}`}>
      <div
        className="h-6 rounded-full bg-neu-bg-primary overflow-hidden"
        style={{
          boxShadow: 'inset 4px 4px 8px #c8c9d4, inset -4px -4px 8px #ffffff',
        }}
      >
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${clampedValue}%`,
            background: 'linear-gradient(90deg, #8b7fc7, #6b5eb0)',
          }}
        />
      </div>
      {showLabel && (
        <p className="text-sm text-neu-text-secondary mt-2 text-center">{clampedValue}% complete</p>
      )}
    </div>
  );
}

// ============================================================================
// AVATAR
// ============================================================================

interface NeuAvatarProps {
  src?: string;
  alt: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fallback?: string;
}

export function NeuAvatar({ src, alt, size = 'md', fallback }: NeuAvatarProps) {
  const sizeClasses = {
    sm: 'w-10 h-10 text-sm',
    md: 'w-16 h-16 text-lg',
    lg: 'w-24 h-24 text-2xl',
    xl: 'w-32 h-32 text-4xl',
  };

  return (
    <div
      className={`${sizeClasses[size]} rounded-full overflow-hidden flex items-center justify-center bg-gradient-to-br from-[#8b7fc7] to-[#6b5eb0] text-white font-bold`}
      style={{
        boxShadow: '4px 4px 8px #c8c9d4, -4px -4px 8px #ffffff',
      }}
    >
      {src ? (
        <img src={src} alt={alt} className="w-full h-full object-cover" />
      ) : (
        <span>{fallback || alt.charAt(0).toUpperCase()}</span>
      )}
    </div>
  );
}

// ============================================================================
// TOAST / NOTIFICATION
// ============================================================================

interface NeuToastProps {
  type: 'success' | 'error' | 'info';
  message: string;
  onClose?: () => void;
}

export function NeuToast({ type, message, onClose }: NeuToastProps) {
  const typeStyles = {
    success: 'bg-[#7bc89d]',
    error: 'bg-red-400',
    info: 'bg-[#8b7fc7]',
  };

  return (
    <div
      className={`${typeStyles[type]} text-white px-6 py-4 rounded-2xl shadow-lg flex items-center gap-4 max-w-md`}
      style={{
        boxShadow: '8px 8px 16px rgba(0,0,0,0.1)',
      }}
    >
      <p className="flex-1 font-medium">{message}</p>
      {onClose && (
        <button onClick={onClose} className="text-white hover:opacity-75 transition-opacity">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}

// ============================================================================
// MODAL
// ============================================================================

interface NeuModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export function NeuModal({ isOpen, onClose, title, children }: NeuModalProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-neu-bg-primary rounded-3xl p-8 max-w-lg w-full max-h-[90vh] overflow-y-auto"
        style={{
          boxShadow: '16px 16px 32px rgba(0,0,0,0.3)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-neu-text-primary">{title}</h2>
          <button
            onClick={onClose}
            className="text-neu-text-secondary hover:text-neu-text-primary transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
