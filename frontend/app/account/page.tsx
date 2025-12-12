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

  const handleManageSubscription = async () => {
    try {
      const portal = await api.createPortalSession();
      window.location.href = portal.url;
    } catch (error) {
      console.error('Portal error:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#e6e7f0] flex items-center justify-center">
        <div className="loader"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#e6e7f0] py-20">
      <div className="container mx-auto px-6 max-w-4xl">
        <h1 className="text-5xl font-bold mb-12">Account Settings</h1>

        {/* Subscription Card */}
        <div className="neu-card rounded-3xl p-8 mb-8">
          <h2 className="text-2xl font-bold mb-6">Subscription</h2>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <p className="text-sm text-[#7a7a8e] mb-1">Current Plan</p>
              <p className="text-2xl font-bold text-[#8b7fc7] capitalize">
                {subscription?.subscription_tier}
              </p>
            </div>

            <div>
              <p className="text-sm text-[#7a7a8e] mb-1">Usage</p>
              <p className="text-2xl font-bold">
                {subscription?.usage_count} / {
                  subscription?.usage_limit === -1
                    ? '∞'
                    : subscription?.usage_limit
                }
              </p>
            </div>

            {subscription?.subscription_status === 'trialing' && (
              <div className="md:col-span-2">
                <p className="text-sm text-[#7a7a8e] mb-1">Trial Ends</p>
                <p className="text-lg font-semibold">
                  {subscription.trial_end
                    ? new Date(subscription.trial_end).toLocaleDateString()
                    : 'N/A'}
                </p>
              </div>
            )}

            {subscription?.current_period_end && subscription?.subscription_tier !== 'free' && (
              <div className="md:col-span-2">
                <p className="text-sm text-[#7a7a8e] mb-1">Next Billing Date</p>
                <p className="text-lg font-semibold">
                  {new Date(subscription.current_period_end).toLocaleDateString()}
                </p>
              </div>
            )}
          </div>

          {subscription?.subscription_tier !== 'free' && (
            <button
              onClick={handleManageSubscription}
              className="neu-button-accent"
            >
              Manage Subscription
            </button>
          )}

          {subscription?.subscription_tier === 'free' && (
            <button
              onClick={() => router.push('/#pricing')}
              className="neu-button-accent"
            >
              Upgrade Plan
            </button>
          )}
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
