'use client'

import { useState } from 'react'
import Header from '@/components/Header'
import ArticleCard from '@/components/ArticleCard'
import CategoryFilters from '@/components/CategoryFilters'
import Pagination from '@/components/Pagination'
import LoadingSpinner from '@/components/LoadingSpinner'
import { useArticles } from '@/hooks/useArticles'
import { RefreshCw, TrendingUp, Zap } from 'lucide-react'

export default function Home() {
  const [showFilters, setShowFilters] = useState(false)
  const {
    articles,
    allArticlesCount,
    filteredArticlesCount,
    categories,
    loading,
    error,
    selectedCategories,
    currentPage,
    totalPages,
    handleSearch,
    handleCategoryToggle,
    handleClearFilters,
    handlePageChange,
    refetch
  } = useArticles()

  const stats = {
    total: filteredArticlesCount,
    categories: categories.length,
    relevance: articles.length > 0
      ? Math.round(articles.reduce((acc, article) => acc + article.relevance_score, 0) / articles.length * 10) / 10
      : 0
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#1a1f2e' }}>

      {/* Header */}
      <Header
        onSearch={handleSearch}
        onFilterToggle={() => setShowFilters(true)}
      />

      {/* Stats Bar */}
      <div className="border-b" style={{ backgroundColor: '#2a3142', borderColor: '#3a4252' }}>
        <div className="container py-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-6">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" style={{ color: '#5b7fff' }} />
                <span className="text-sm font-medium" style={{ color: '#ffffff' }}>
                  {filteredArticlesCount} Articles
                  {selectedCategories.length > 0 && (
                    <span className="ml-1 opacity-70">
                      (filtered from {allArticlesCount})
                    </span>
                  )}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5" style={{ color: '#ff5b7f' }} />
                <span className="text-sm font-medium" style={{ color: '#ffffff' }}>
                  {stats.categories} Categories
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <RefreshCw className="w-5 h-5" style={{ color: '#7fff5b' }} />
                <span className="text-sm font-medium" style={{ color: '#ffffff' }}>
                  Avg Score: {stats.relevance}/5
                </span>
              </div>
            </div>

            {selectedCategories.length > 0 && (
              <button
                onClick={handleClearFilters}
                className="text-xs px-3 py-1 rounded-full transition-colors hover:opacity-80"
                style={{
                  backgroundColor: 'rgba(255, 91, 127, 0.2)',
                  color: '#ff5b7f'
                }}
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Category Filters */}
      <CategoryFilters
        categories={categories}
        selectedCategories={selectedCategories}
        onCategoryToggle={handleCategoryToggle}
        onClearAll={handleClearFilters}
      />

      {/* Main Content */}
      <main className="container py-8">
        {loading ? (
          <LoadingSpinner />
        ) : error ? (
          <div className="text-center py-12">
            <div className="text-red-500 mb-4">{error}</div>
            <button
              onClick={refetch}
              className="px-4 py-2 rounded-lg text-white"
              style={{ backgroundColor: '#5b7fff' }}
            >
              Try Again
            </button>
          </div>
        ) : articles.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-2xl font-bold mb-2" style={{ color: '#ffffff' }}>
              No articles found
            </div>
            <p className="mb-4" style={{ color: '#a0a4b8' }}>
              {selectedCategories.length > 0
                ? 'Try selecting different categories or clearing filters.'
                : 'Try adjusting your search terms.'
              }
            </p>
            {selectedCategories.length > 0 && (
              <button
                onClick={handleClearFilters}
                className="px-4 py-2 rounded-lg text-white"
                style={{ backgroundColor: '#5b7fff' }}
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {/* Article Grid */}
            <div className="grid gap-6">
              {articles.map((article, index) => (
                <div
                  key={article.id}
                  className="animate-fade-in"
                  style={{
                    animationDelay: `${index * 50}ms`,
                    animationFillMode: 'both'
                  }}
                >
                  <ArticleCard article={article} />
                </div>
              ))}
            </div>

            {/* Pagination */}
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalItems={filteredArticlesCount}
              itemsPerPage={12}
              onPageChange={handlePageChange}
            />
          </div>
        )}
      </main>

      {/* Legacy Filters Panel (hidden for now) */}
      <div style={{ display: 'none' }}>
        <div
          className="fixed right-0 top-0 h-full w-full sm:w-96 shadow-2xl z-50"
          style={{ backgroundColor: '#2a3142' }}
        >
          {/* This keeps the component in memory but hidden */}
        </div>
      </div>

    </div>
  )
}