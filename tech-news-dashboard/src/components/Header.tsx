'use client'

import { Search, Filter, TrendingUp } from 'lucide-react'
import { useState } from 'react'

interface HeaderProps {
  onSearch: (query: string) => void
  onFilterToggle: () => void
}

export default function Header({ onSearch, onFilterToggle }: HeaderProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch(searchQuery)
  }

  return (
    <header className="sticky top-0 z-50 backdrop-blur-lg bg-opacity-90" style={{ backgroundColor: '#1a1f2e' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-8 w-8" style={{ color: '#5b7fff' }} />
              <h1 className="text-2xl font-bold" style={{ color: '#ffffff' }}>
                TechNews
              </h1>
            </div>
            <span className="text-sm" style={{ color: '#a0a4b8' }}>
              Dashboard
            </span>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl mx-8">
            <form onSubmit={handleSearch} className="relative">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5" style={{ color: '#a0a4b8' }} />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full pl-10 pr-4 py-2 rounded-xl border transition-all duration-200 focus:outline-none focus:ring-2"
                  style={{
                    backgroundColor: '#2a3142',
                    borderColor: '#3a4252',
                    color: '#ffffff',
                    focusRingColor: '#5b7fff',
                  }}
                  placeholder="Search articles..."
                />
              </div>
            </form>
          </div>

          {/* Filter Button */}
          <button
            onClick={onFilterToggle}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-200 hover:scale-105"
            style={{
              backgroundColor: '#2a3142',
              color: '#ffffff',
              border: '1px solid #3a4252',
            }}
          >
            <Filter className="h-4 w-4" />
            <span className="hidden sm:inline">Filters</span>
          </button>
        </div>
      </div>
    </header>
  )
}