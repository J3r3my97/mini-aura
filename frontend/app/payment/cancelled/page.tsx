'use client';

import { useRouter } from 'next/navigation';

export default function PaymentCancelled() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-[#e6e7f0] flex items-center justify-center p-6">
      <div className="neu-card rounded-3xl p-12 max-w-md text-center">
        <div className="w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>

        <h1 className="text-3xl font-bold mb-4">Payment Cancelled</h1>
        <p className="text-[#7a7a8e] mb-8">
          Your payment was cancelled. No charges have been made.
        </p>

        <div className="flex flex-col gap-4">
          <button
            onClick={() => router.push('/#pricing')}
            className="neu-button-accent w-full"
          >
            View Pricing Again
          </button>
          <button
            onClick={() => router.push('/')}
            className="neu-button w-full"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
