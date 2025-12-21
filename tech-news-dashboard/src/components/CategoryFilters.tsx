'use client'

import { useState } from 'react'
import { ChevronDown, X } from 'lucide-react'

interface Category {
  id: string
  name: string
  article_count: number
}

interface CategoryFiltersProps {
  categories: Category[]
  selectedCategories: string[]
  onCategoryToggle: (category: string) => void
  onClearAll: () => void
}

export default function CategoryFilters({
  categories,
  selectedCategories,
  onCategoryToggle,
  onClearAll
}: CategoryFiltersProps) {
  const [showMore, setShowMore] = useState(false)

  const displayedCategories = showMore ? categories : categories.slice(0, 8)

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
    <div className="w-full border-b" style={{ backgroundColor: '#2a3142', borderColor: '#3a4252' }}>
      <div className="container py-4">
        <div className="flex flex-col gap-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <h3 className="font-semibold text-sm uppercase tracking-wider" style={{ color: '#ffffff' }}>
                Filter by Category
              </h3>
              <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: '#3a4252', color: '#a0a4b8' }}>
                {categories.length} categories
              </span>
            </div>

            {selectedCategories.length > 0 && (
              <button
                onClick={onClearAll}
                className="flex items-center space-x-1 text-xs px-3 py-1 rounded-lg transition-colors hover:opacity-80"
                style={{
                  backgroundColor: 'rgba(255, 91, 127, 0.2)',
                  color: '#ff5b7f'
                }}
              >
                <X className="w-3 h-3" />
                <span>Clear all ({selectedCategories.length})</span>
              </button>
            )}
          </div>

          {/* Category Pills */}
          <div className="flex flex-wrap gap-2">
            {displayedCategories.map((category) => {
              const isSelected = selectedCategories.includes(category.name)
              const categoryColor = getCategoryColor(category.name)

              return (
                <button
                  key={category.id}
                  onClick={() => onCategoryToggle(category.name)}
                  className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 hover:scale-105"
                  style={{
                    backgroundColor: isSelected
                      ? categoryColor
                      : 'rgba(255, 255, 255, 0.1)',
                    color: isSelected
                      ? '#1a1f2e'
                      : '#ffffff',
                    border: isSelected
                      ? 'none'
                      : `1px solid ${categoryColor}40`,
                  }}
                >
                  <span>{category.name}</span>
                  <span className="ml-2 text-xs opacity-70">
                    ({category.article_count})
                  </span>
                </button>
              )
            })}

            {categories.length > 8 && (
              <button
                onClick={() => setShowMore(!showMore)}
                className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium transition-all duration-200"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  color: '#a0a4b8',
                  border: '1px dashed #3a4252'
                }}
              >
                {showMore ? (
                  <>Show less</>
                ) : (
                  <>
                    Show more
                    <ChevronDown className="w-4 h-4 ml-1" />
                  </>
                )}
              </button>
            )}
          </div>

          {/* Active Filters Display */}
          {selectedCategories.length > 0 && (
            <div className="flex items-center gap-2 pt-2 border-t" style={{ borderColor: '#3a4252' }}>
              <span className="text-xs" style={{ color: '#a0a4b8' }}>Active filters:</span>
              <div className="flex flex-wrap gap-1">
                {selectedCategories.map((category) => (
                  <span
                    key={category}
                    className="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
                    style={{
                      backgroundColor: `${getCategoryColor(category)}20`,
                      color: getCategoryColor(category)
                    }}
                  >
                    {category}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}