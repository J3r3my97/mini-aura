'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import api, { SubscriptionStatus } from '@/lib/api';

export default function PaymentSuccess() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await api.getSubscriptionStatus();
        setSubscription(status);
      } catch (error) {
        console.error('Error fetching subscription:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  const handleContinue = () => {
    router.push('/');
  };

  return (
    <div className="min-h-screen bg-[#e6e7f0] flex items-center justify-center p-6">
      <div className="neu-card rounded-3xl p-12 max-w-md text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <h1 className="text-3xl font-bold mb-4">Payment Successful!</h1>

        {loading ? (
          <p className="text-[#7a7a8e] mb-8">Loading your subscription...</p>
        ) : (
          <>
            <p className="text-[#7a7a8e] mb-2">
              You're now on the <span className="font-bold text-[#8b7fc7] capitalize">{subscription?.subscription_tier}</span> plan
            </p>
            {subscription?.subscription_status === 'trialing' && (
              <p className="text-sm text-[#7a7a8e] mb-8">
                Your 7-day free trial is active. You won't be charged until {
                  subscription.current_period_end
                    ? new Date(subscription.current_period_end).toLocaleDateString()
                    : 'trial ends'
                }
              </p>
            )}
            <p className="text-[#7a7a8e] mb-8">
              {subscription?.usage_limit === -1
                ? 'Enjoy unlimited avatar generations!'
                : `You have ${subscription ? subscription.usage_limit - subscription.usage_count : 0} avatars remaining.`
              }
            </p>
          </>
        )}

        <button
          onClick={handleContinue}
          className="neu-button-accent w-full"
        >
          Start Creating Avatars
        </button>
      </div>
    </div>
  );
}
