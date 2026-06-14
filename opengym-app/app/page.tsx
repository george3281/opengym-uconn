'use client'

import { useEffect, useMemo, useState } from 'react'
import {
  fetchLive,
  fetchDay,
  fetchWeather,
  todayIdx,
  semesterProgress,
  type HourSlot,
} from '@/lib/api'
import OccupancyHero from '@/components/Occupancy'
import HourlyForecast from '@/components/Forecast'
import WeeklyHeatmap from '@/components/Heatmap'
import TodaySummary from '@/components/Summary'
import Chart from '@/components/Chart'

export default function Home() {
  const [hour, setHour] = useState<number | null>(null)
  const [live, setLive] = useState<{ occupancy: number; closed: boolean } | null>(null)
  const [today, setToday] = useState<HourSlot[]>([])
  const [heatmap, setHeatmap] = useState<HourSlot[][]>([])

  useEffect(() => {
    const h = new Date().getHours()
    setHour(h)

    fetchLive()
      .then((r) => setLive({ occupancy: r.is_closed ? 0 : r.occupancy, closed: r.is_closed }))
      .catch(() => setLive({ occupancy: 0, closed: false }))

    ;(async () => {
      const idx = todayIdx()
      const sp = semesterProgress()
      const { weather, temperature } = await fetchWeather()
      const [d0, d1, d2, d3, d4] = await Promise.all([
        fetchDay(0, idx, sp, weather, temperature),
        fetchDay(1, idx, sp, weather, temperature),
        fetchDay(2, idx, sp, weather, temperature),
        fetchDay(3, idx, sp, weather, temperature),
        fetchDay(4, idx, sp, weather, temperature),
      ])
      setToday(d0)
      setHeatmap([[], d1, d2, d3, d4])
    })().catch(() => setLive({ occupancy: 0, closed: false }))
  }, [])

  const todayWithLive = useMemo(() => {
    if (hour === null || !today.length || !live) return today
    const slot: HourSlot = { hour, occupancy: live.occupancy, live: true }
    return today.some((s) => s.hour === hour)
      ? today.map((s) => (s.hour === hour ? slot : s))
      : [...today, slot].sort((a, b) => a.hour - b.hour)
  }, [today, hour, live])

  const hourlyDays = useMemo(() => {
    if (hour === null || !todayWithLive.length) return []
    const hours = todayWithLive.filter((s) => s.hour >= hour && s.hour <= 22)
    const days = [{ offset: 0, hours }]
    const tomorrow = heatmap[1]
    if (tomorrow?.length) days.push({ offset: 1, hours: tomorrow })
    return days
  }, [todayWithLive, heatmap, hour])

  const openHours = today.filter((s) => s.hour >= 8 && s.hour <= 20)
  const peak = openHours.length ? Math.round(Math.max(...openHours.map((s) => s.occupancy)) * 100) : null
  const quietest = openHours.length
    ? openHours.reduce((a, b) => (a.occupancy < b.occupancy ? a : b))
    : null

  return (
    <main className="min-h-dvh w-full bg-[#0f0f0f]">
      <div className="w-full max-w-100 mx-auto pb-12 px-[max(0.75rem,3vw)]">
        {live === null ? (
          <p className="text-gray-600 text-sm animate-pulse h-56 flex items-center justify-center">Loading...</p>
        ) : (
          <OccupancyHero occupancy={live.occupancy} closed={live.closed} />
        )}

        <div className="bg-zinc-900 rounded-2xl p-4 mb-3">
          {peak !== null && quietest ? (
            <TodaySummary peak={peak} quietest={quietest} />
          ) : (
            <p className="text-gray-600 text-sm animate-pulse mb-3">Loading...</p>
          )}

          {hourlyDays.length > 0 && hour !== null && (
            <HourlyForecast days={hourlyDays} hour={hour} />
          )}

          {todayWithLive.length > 0 && hour !== null && (
            <Chart forecast={todayWithLive} hour={hour} />
          )}
        </div>

        <div className="bg-zinc-900 rounded-2xl p-4 mb-3">
          <p className="text-white font-medium text-sm mb-1">What to Expect This Week</p>
          <p className="text-[10px] text-gray-500 mb-3">Predicted occupancy for the next 4 days</p>
          {heatmap.length > 0 ? (
            <WeeklyHeatmap data={heatmap} />
          ) : (
            <p className="text-gray-600 text-sm animate-pulse">Loading...</p>
          )}
        </div>

        <p className="text-xs text-gray-500 mt-6 text-center">
          Created by{' '}
          <a href="https://github.com/george3281" target="_blank" rel="noreferrer" className="hover:text-gray-400">
            george3281
          </a>
        </p>
      </div>
    </main>
  )
}
