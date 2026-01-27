'use client'

import 'bootstrap-icons/font/bootstrap-icons.css'
import { useEffect, useRef, useState } from 'react'

function Pill({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/70 backdrop-blur-sm ring-1 ring-black/10 shadow-sm">
      <span className="text-slate-700">{icon}</span>
      <span className="text-sm font-medium text-slate-700">{label}</span>
    </div>
  )
}

function ImagePlaceholder({ label }: { label: string }) {
  return (
    <div className="relative w-full rounded-2xl bg-white/80 ring-1 ring-black/5 shadow-[0_18px_40px_rgba(0,0,0,0.12)] overflow-hidden">
      {/* 16:9-ish placeholder area */}
      <div className="aspect-[16/9] w-full bg-gradient-to-b from-slate-50 to-slate-100" />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="px-4 py-2 rounded-full bg-white/80 backdrop-blur-sm ring-1 ring-black/10 text-sm text-slate-600">
          {label} (image placeholder)
        </div>
      </div>
    </div>
  )
}

function FeatureText({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="rounded-2xl bg-white/75 backdrop-blur-sm ring-1 ring-black/5 shadow-[0_14px_30px_rgba(0,0,0,0.10)] p-8">
      <div className="flex items-center gap-3">
        <div className="text-2xl text-vedya-purple">{icon}</div>
        <h3 className="text-2xl font-semibold text-slate-900">{title}</h3>
      </div>
      <p className="mt-4 text-slate-700 leading-relaxed">{description}</p>
    </div>
  )
}

function TagPill({ children, muted }: { children: React.ReactNode; muted?: boolean }) {
  return (
    <div
      className={[
        'px-7 py-3 rounded-full text-base',
        'ring-1 ring-black/10 hover:ring-black/15',
        'bg-white/45 backdrop-blur-sm hover:bg-white',
        'shadow-none hover:shadow-[0_10px_24px_rgba(0,0,0,0.10)]',
        'transition-all duration-200 ease-out hover:scale-105',
        'text-slate-900',
      ].join(' ')}
    >
      {children}
    </div>
  )
}

type Tag = { label: string; muted?: boolean }

export default function InsightsSection() {
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef<HTMLElement | null>(null)

  const tags: Tag[] = [
    { label: 'Customer Retention', muted: true },
    { label: 'Seamless Integrations' },
    { label: 'Real-Time Reports' },
    { label: 'Personalized Engagement' },
    { label: 'Cost-Effective', muted: true },
    { label: 'Smart Spending' },
    { label: 'Data-Driven Decisions' },
    { label: 'Increased Efficiency' },
  ]

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      {
        threshold: 0.15,
        rootMargin: '0px 0px -80px 0px',
      }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  return (
    <section ref={sectionRef} className="relative py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div
          className={`text-center transition-all duration-1000 ease-out ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
            }`}
        >
          <Pill icon={<i className="bi bi-search" />} label="Live Oversight" />
          <h2 className="mt-6 text-5xl md:text-6xl font-semibold tracking-tight text-slate-900">
            Comprehensive Insights
          </h2>
          <p className="mt-4 text-base md:text-lg text-slate-700">
            Track every campaign and customer interaction to refine engagement strategies
          </p>
        </div>

        {/* Chart placeholders row */}
        <div
          className={`
            mt-12 grid grid-cols-1 lg:grid-cols-2 gap-8
            transition-all duration-1000 ease-out
            ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}
          `}
          style={{ transitionDelay: '150ms' }}
        >
          <ImagePlaceholder label="Chart panel A" />
          <ImagePlaceholder label="Chart panel B" />
        </div>

        {/* Tag pills - infinite marquee (left -> right) */}
        <div
          className={`
            mt-14 space-y-10
            transition-all duration-1000 ease-out
            ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}
          `}
          style={{ transitionDelay: '300ms' }}
        >
          {/* Row 1: left -> right */}
          <div className="marquee">
            <div className="marquee__track">
              <div className="flex items-center gap-6 pr-6">
                {tags.map((t) => (
                  <TagPill key={`a1-${t.label}`} muted={t.muted}>
                    {t.label}
                  </TagPill>
                ))}
              </div>
              <div className="flex items-center gap-6 pr-6" aria-hidden="true">
                {tags.map((t) => (
                  <TagPill key={`b1-${t.label}`} muted={t.muted}>
                    {t.label}
                  </TagPill>
                ))}
              </div>
            </div>
          </div>

          {/* Row 2: right -> left */}
          <div className="marquee">
            <div className="marquee__track marquee__track--reverse">
              <div className="flex items-center gap-6 pr-6">
                {tags.map((t) => (
                  <TagPill key={`a2-${t.label}`} muted={t.muted}>
                    {t.label}
                  </TagPill>
                ))}
              </div>
              <div className="flex items-center gap-6 pr-6" aria-hidden="true">
                {tags.map((t) => (
                  <TagPill key={`b2-${t.label}`} muted={t.muted}>
                    {t.label}
                  </TagPill>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}


