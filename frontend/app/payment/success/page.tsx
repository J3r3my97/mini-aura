import { Suspense } from 'react';
import PaymentSuccessContent from './PaymentSuccessContent';

export default function PaymentSuccess() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#e6e7f0] flex items-center justify-center p-6">
        <div className="neu-card rounded-3xl p-12 max-w-md text-center">
          <p className="text-[#7a7a8e]">Loading...</p>
        </div>
      </div>
    }>
      <PaymentSuccessContent />
    </Suspense>
  );
}
