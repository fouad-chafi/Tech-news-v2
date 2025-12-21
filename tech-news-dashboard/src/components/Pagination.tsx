'use client'

import { ChevronLeft, ChevronRight } from 'lucide-react'

interface PaginationProps {
  currentPage: number
  totalPages: number
  totalItems: number
  itemsPerPage: number
  onPageChange: (page: number) => void
}

export default function Pagination({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange
}: PaginationProps) {
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  const getVisiblePages = () => {
    const pages: number[] = []
    const showEllipsis = totalPages > 7

    if (!showEllipsis) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }

    if (currentPage <= 3) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push(-1) // Ellipsis
      pages.push(totalPages)
    } else if (currentPage >= totalPages - 2) {
      pages.push(1)
      pages.push(-1) // Ellipsis
      for (let i = totalPages - 4; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push(-1) // Ellipsis
      for (let i = currentPage - 1; i <= currentPage + 1; i++) {
        pages.push(i)
      }
      pages.push(-1) // Ellipsis
      pages.push(totalPages)
    }

    return pages
  }

  if (totalPages <= 1) return null

  return (
    <div className="flex flex-col items-center gap-4 py-8">
      {/* Info */}
      <div className="text-sm" style={{ color: '#a0a4b8' }}>
        Showing {startItem}-{endItem} of {totalItems} articles
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center space-x-1">
        {/* Previous Button */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            backgroundColor: currentPage === 1 ? '#2a3142' : '#3a4252',
            color: currentPage === 1 ? '#4a5262' : '#ffffff',
          }}
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Previous
        </button>

        {/* Page Numbers */}
        <div className="flex items-center space-x-1">
          {getVisiblePages().map((page, index) => (
            <div key={index}>
              {page === -1 ? (
                <span className="px-2" style={{ color: '#a0a4b8' }}>...</span>
              ) : (
                <button
                  onClick={() => onPageChange(page as number)}
                  className={`w-10 h-10 rounded-lg text-sm font-medium transition-all duration-200`}
                  style={{
                    backgroundColor: currentPage === page
                      ? '#5b7fff'
                      : '#3a4252',
                    color: currentPage === page
                      ? '#1a1f2e'
                      : '#ffffff',
                  }}
                >
                  {page}
                </button>
              )}
            </div>
          ))}
        </div>

        {/* Next Button */}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            backgroundColor: currentPage === totalPages ? '#2a3142' : '#3a4252',
            color: currentPage === totalPages ? '#4a5262' : '#ffffff',
          }}
        >
          Next
          <ChevronRight className="w-4 h-4 ml-1" />
        </button>
      </div>
    </div>
  )
}