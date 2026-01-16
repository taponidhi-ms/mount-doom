'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export type TimezoneOption = 'UTC' | 'IST'

interface TimezoneContextType {
  timezone: TimezoneOption
  setTimezone: (tz: TimezoneOption) => void
  formatTimestamp: (timestamp: string | Date) => string
  formatTime: (timestamp: string | Date) => string
}

const TimezoneContext = createContext<TimezoneContextType | undefined>(undefined)

const TIMEZONE_KEY = 'mount-doom-timezone'

export function TimezoneProvider({ children }: { children: ReactNode }) {
  const [timezone, setTimezoneState] = useState<TimezoneOption>('IST')

  useEffect(() => {
    // Load saved timezone preference from localStorage
    const saved = localStorage.getItem(TIMEZONE_KEY) as TimezoneOption
    if (saved && (saved === 'UTC' || saved === 'IST')) {
      setTimezoneState(saved)
    }
  }, [])

  const setTimezone = (tz: TimezoneOption) => {
    setTimezoneState(tz)
    localStorage.setItem(TIMEZONE_KEY, tz)
  }

  const formatTimestamp = (timestamp: string | Date): string => {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp
    
    if (timezone === 'UTC') {
      return date.toLocaleString('en-US', {
        timeZone: 'UTC',
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      }) + ' UTC'
    } else {
      return date.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      }) + ' IST'
    }
  }

  const formatTime = (timestamp: string | Date): string => {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp
    
    if (timezone === 'UTC') {
      return date.toLocaleTimeString('en-US', {
        timeZone: 'UTC',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      })
    } else {
      return date.toLocaleTimeString('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      })
    }
  }

  return (
    <TimezoneContext.Provider value={{ timezone, setTimezone, formatTimestamp, formatTime }}>
      {children}
    </TimezoneContext.Provider>
  )
}

export function useTimezone() {
  const context = useContext(TimezoneContext)
  if (context === undefined) {
    throw new Error('useTimezone must be used within a TimezoneProvider')
  }
  return context
}
