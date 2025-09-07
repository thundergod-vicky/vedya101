'use client';

import { useSearchParams } from 'next/navigation';
import TeachingInterface from '@/components/TeachingInterface';
import Navbar from '@/components/Navbar';
import { Suspense } from 'react';

function TeachingPageInner() {
  const searchParams = useSearchParams();
  const planId = searchParams.get('plan') || 'plan_1'; // Default fallback
  return <TeachingInterface planId={planId} />;
}

export default function TeachingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar showBackButton={true} />
      <Suspense fallback={<div className="p-6 text-sm text-gray-600">Loading teaching interface...</div>}>
        <TeachingPageInner />
      </Suspense>
    </div>
  );
}
