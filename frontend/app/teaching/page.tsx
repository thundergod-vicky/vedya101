'use client';

import { useSearchParams } from 'next/navigation';
import TeachingInterface from '@/components/TeachingInterface';
import Navbar from '@/components/Navbar';

export default function TeachingPage() {
  const searchParams = useSearchParams();
  const planId = searchParams.get('plan') || 'plan_1'; // Default fallback

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar showBackButton={true} />
      <TeachingInterface planId={planId} />
    </div>
  );
}
