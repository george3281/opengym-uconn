'use client'

import { useEffect, useRef } from 'react'
import { Chart as ChartJS, registerables } from 'chart.js'
import { formatHour, type HourSlot } from '@/lib/api'

ChartJS.register(...registerables)

export default function Chart({ forecast, hour }: { forecast: HourSlot[]; hour: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const chartRef = useRef<ChartJS | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !forecast.length) return

    chartRef.current?.destroy()
    const liveIdx = forecast.findIndex((f) => f.hour === hour && f.live)
    const predictedData = forecast.map((f, i) => (i === liveIdx ? null : Math.round(f.occupancy * 100)))
    const liveData = forecast.map((f, i) => (i === liveIdx ? Math.round(f.occupancy * 100) : null))

    chartRef.current = new ChartJS(canvas, {
      type: 'line',
      data: {
        labels: forecast.map((f) => formatHour(f.hour)),
        datasets: [
          {
            label: 'Predicted',
            data: predictedData,
            borderColor: '#3b82f6',
            borderWidth: 2,
            borderDash: [4, 4],
            fill: true,
            backgroundColor: (ctx) => {
              const { chartArea, ctx: c } = ctx.chart
              if (!chartArea) return 'rgba(59,130,246,0.15)'
              const g = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
              g.addColorStop(0, 'rgba(59,130,246,0.15)')
              g.addColorStop(1, 'rgba(59,130,246,0)')
              return g
            },
            tension: 0.4,
            pointRadius: 0,
            spanGaps: true,
          },
          {
            label: 'Live',
            data: liveData,
            borderColor: '#d4d4d8',
            borderWidth: 2,
            backgroundColor: '#d4d4d8',
            pointRadius: 2,
            pointHoverRadius: 2,
            showLine: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#6b7280', font: { size: 9 }, maxRotation: 0, maxTicksLimit: 6 },
            border: { display: false },
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.06)' },
            ticks: { color: '#6b7280', font: { size: 9 }, callback: (v) => `${v}%`, maxTicksLimit: 4 },
            border: { display: false },
            min: 0,
            max: 100,
          },
        },
      },
    })

    return () => {
      chartRef.current?.destroy()
      chartRef.current = null
    }
  }, [forecast, hour])

  const hasLive = forecast.some((f) => f.hour === hour && f.live)

  return (
    <div className="relative h-[130px] w-full mt-3 pt-3 border-t border-zinc-700 flex flex-col">
      <div className="flex items-center gap-3 mb-2 shrink-0">
        <div className="flex items-center gap-1">
          <span className="w-2 border-t-1 border-dashed border-blue-500" />
          <span className="text-[10px] text-gray-500">Predicted</span>
        </div>
        {hasLive && (
          <div className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-300" />
            <span className="text-[10px] text-gray-500">Actual</span>
          </div>
        )}
      </div>
      <div className="flex-1 min-h-0">
        <canvas ref={canvasRef} />
      </div>
    </div>
  )
}
