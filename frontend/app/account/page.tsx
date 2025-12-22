'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import api, { SubscriptionStatus } from '@/lib/api';

export default function Account() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      router.push('/');
      return;
    }

    fetchSubscription();
  }, [user, router]);

  const fetchSubscription = async () => {
    try {
      const status = await api.getSubscriptionStatus();
      setSubscription(status);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#e6e7f0] flex items-center justify-center">
        <div className="loader"></div>
      </div>
    );
  }

  const freeCreditsRemaining = 1 - (subscription?.free_credits_used || 0);

  return (
    <div className="min-h-screen bg-[#e6e7f0] py-20">
      <div className="container mx-auto px-6 max-w-4xl">
        <h1 className="text-5xl font-bold mb-12">Account Settings</h1>

        {/* Credits Card */}
        <div className="neu-card rounded-3xl p-8 mb-8">
          <h2 className="text-2xl font-bold mb-6">Credits & Usage</h2>

          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div>
              <p className="text-sm text-[#7a7a8e] mb-1">Available Credits</p>
              <p className="text-3xl font-bold text-[#8b7fc7]">
                {subscription?.credits || 0}
              </p>
              <p className="text-xs text-[#7a7a8e] mt-1">Paid credits (no watermark)</p>
            </div>

            <div>
              <p className="text-sm text-[#7a7a8e] mb-1">Free Credits</p>
              <p className="text-3xl font-bold text-[#7bc89d]">
                {freeCreditsRemaining}
              </p>
              <p className="text-xs text-[#7a7a8e] mt-1">Remaining (with watermark)</p>
            </div>

            <div>
              <p className="text-sm text-[#7a7a8e] mb-1">Total Generated</p>
              <p className="text-3xl font-bold">
                {subscription?.total_generated || 0}
              </p>
              <p className="text-xs text-[#7a7a8e] mt-1">All-time avatars</p>
            </div>
          </div>

          {subscription && subscription.credits === 0 && freeCreditsRemaining === 0 && (
            <div className="bg-[#8b7fc7]/10 border border-[#8b7fc7]/30 rounded-2xl p-4 mb-6">
              <p className="text-[#4a4a5e] font-medium">
                ⚠️ You're out of credits. Purchase more to continue generating avatars!
              </p>
            </div>
          )}

          <button
            onClick={() => router.push('/#pricing')}
            className="neu-button-accent"
          >
            Purchase More Credits
          </button>
        </div>

        {/* Account Info */}
        <div className="neu-card rounded-3xl p-8">
          <h2 className="text-2xl font-bold mb-6">Account Information</h2>

          <div className="mb-6">
            <p className="text-sm text-[#7a7a8e] mb-1">Email</p>
            <p className="text-lg">{user?.email}</p>
          </div>

          <button onClick={logout} className="neu-button">
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
