import { X, ChevronDown } from 'lucide-react'
import { useState } from 'react'

interface Category {
  id: string
  name: string
  article_count: number
}

interface FiltersProps {
  categories: Category[]
  selectedCategories: string[]
  onCategoryToggle: (category: string) => void
  onClearFilters: () => void
  isOpen: boolean
  onClose: () => void
}

export default function Filters({
  categories,
  selectedCategories,
  onCategoryToggle,
  onClearFilters,
  isOpen,
  onClose
}: FiltersProps) {
  const [sortBy, setSortBy] = useState<'recent' | 'relevance'>('recent')

  if (!isOpen) return null

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      AI: '#5b7fff',
      TOOLS: '#ff5b7f',
      DEV: '#7fff5b',
      WEB: '#ffdf5b',
      CLOUD: '#5bffdf',
      CYBERSECURITY: '#df5bff',
      MOBILE: '#ff8c5b',
      STARTUPS: '#5bffff',
      OPEN_SOURCE: '#ffd35b',
      NEWS: '#8b5bff',
    }
    return colors[category] || '#5b7fff'
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Filter Panel */}
      <div className="fixed right-0 top-0 h-full w-full sm:w-96 shadow-2xl z-50 animate-slide-up">
        <div className="h-full flex flex-col" style={{ backgroundColor: '#2a3142' }}>

          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b" style={{ borderColor: '#3a4252' }}>
            <h2 className="text-xl font-bold" style={{ color: '#ffffff' }}>
              Filters
            </h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg transition-colors hover:bg-opacity-10 hover:bg-gray-500"
            >
              <X className="w-5 h-5" style={{ color: '#a0a4b8' }} />
            </button>
          </div>

          {/* Filter Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">

            {/* Sort Options */}
            <div>
              <h3 className="text-sm font-semibold mb-3 uppercase tracking-wider" style={{ color: '#a0a4b8' }}>
                Sort By
              </h3>
              <div className="space-y-2">
                {[
                  { value: 'recent', label: 'Most Recent' },
                  { value: 'relevance', label: 'Most Relevant' }
                ].map((option) => (
                  <label
                    key={option.value}
                    className="flex items-center p-3 rounded-lg cursor-pointer transition-colors hover:bg-opacity-10 hover:bg-gray-500"
                  >
                    <input
                      type="radio"
                      name="sort"
                      value={option.value}
                      checked={sortBy === option.value}
                      onChange={(e) => setSortBy(e.target.value as 'recent' | 'relevance')}
                      className="w-4 h-4 text-blue-500 rounded focus:ring-blue-500"
                      style={{ accentColor: '#5b7fff' }}
                    />
                    <span className="ml-3" style={{ color: '#ffffff' }}>
                      {option.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Categories */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold uppercase tracking-wider" style={{ color: '#a0a4b8' }}>
                  Categories
                </h3>
                {selectedCategories.length > 0 && (
                  <button
                    onClick={onClearFilters}
                    className="text-xs font-medium px-3 py-1 rounded-full transition-colors"
                    style={{
                      backgroundColor: '#5b7fff20',
                      color: '#5b7fff'
                    }}
                  >
                    Clear All
                  </button>
                )}
              </div>
              <div className="space-y-2">
                {categories.slice(0, 10).map((category) => (
                  <label
                    key={category.id}
                    className="flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all duration-200 hover:bg-opacity-10 hover:bg-gray-500"
                  >
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedCategories.includes(category.name)}
                        onChange={() => onCategoryToggle(category.name)}
                        className="w-4 h-4 rounded focus:ring-2 focus:ring-blue-500"
                        style={{ accentColor: getCategoryColor(category.name) }}
                      />
                      <div className="ml-3 flex items-center space-x-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: getCategoryColor(category.name) }}
                        />
                        <span style={{ color: '#ffffff' }}>
                          {category.name}
                        </span>
                      </div>
                    </div>
                    <span className="text-xs px-2 py-1 rounded-full bg-gray-700" style={{ color: '#a0a4b8' }}>
                      {category.article_count}
                    </span>
                  </label>
                ))}
              </div>
            </div>

          </div>

          {/* Footer with Apply Button */}
          <div className="p-6 border-t" style={{ borderColor: '#3a4252' }}>
            <button
              onClick={onClose}
              className="w-full py-3 px-4 rounded-xl font-semibold transition-all duration-200 hover:scale-[1.02] shadow-lg"
              style={{
                backgroundColor: '#5b7fff',
                color: '#ffffff'
              }}
            >
              Apply Filters
            </button>
          </div>

        </div>
      </div>
    </>
  )
}