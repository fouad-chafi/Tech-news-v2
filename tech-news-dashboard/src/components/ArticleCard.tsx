'use client'

import { useState } from 'react'
import { Calendar, ExternalLink, ChevronRight, FileText, Code, Globe, Zap } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { Article } from '@/lib/supabase'

interface ArticleCardProps {
  article: Article
}

export default function ArticleCard({ article }: ArticleCardProps) {
  const [imageError, setImageError] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)

  // Decode HTML entities in image URL
  const decodedImageUrl = article.image_url ? article.image_url.replace(/&#038;/g, '&').replace(/&amp;/g, '&') : ''

  // DEBUG: Log pour comprendre
  console.log('=== ArticleCard DEBUG ===')
  console.log('Article:', article.title)
  console.log('Original Image URL:', article.image_url)
  console.log('Decoded Image URL:', decodedImageUrl)
  console.log('Has Valid Image:', !!decodedImageUrl && decodedImageUrl.trim() !== '')
  console.log('Image Error:', imageError)
  console.log('Image Loaded:', imageLoaded)
  console.log('=== END DEBUG ===')

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

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return formatDistanceToNow(date, { addSuffix: true })
    } catch {
      return 'Unknown date'
    }
  }

  const getPlaceholderImage = (sourceName: string) => {
    const hash = sourceName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    const patterns = [
      { icon: Code, gradient: 'from-blue-500 to-purple-600' },
      { icon: Globe, gradient: 'from-green-500 to-teal-600' },
      { icon: Zap, gradient: 'from-orange-500 to-red-600' },
      { icon: FileText, gradient: 'from-indigo-500 to-blue-600' },
    ]
    const pattern = patterns[hash % patterns.length]
    const Icon = pattern.icon

    return (
      <div className={`absolute inset-0 bg-gradient-to-br ${pattern.gradient} flex items-center justify-center`}>
        <Icon className="w-12 h-12 text-white opacity-80" />
      </div>
    )
  }

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    console.log('IMAGE ERROR for:', decodedImageUrl, 'Error:', e)
    setImageError(true)
  }

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    console.log('IMAGE LOADED for:', decodedImageUrl, 'Natural size:', e.currentTarget.naturalWidth, 'x', e.currentTarget.naturalHeight)
    setImageLoaded(true)
  }

  // Permissive: Trust all URLs from database, only show placeholder if really no image
  const hasValidImage = decodedImageUrl && decodedImageUrl.trim() !== ''
  const shouldShowPlaceholder = !hasValidImage || imageError

  // DEBUG: Log final state
  console.log('Final State:')
  console.log('hasValidImage:', hasValidImage)
  console.log('shouldShowPlaceholder:', shouldShowPlaceholder)
  console.log('=== FINAL DEBUG ===')

  return (
    <article className="group relative transition-all duration-300 hover:scale-[1.02] hover:shadow-card-hover">
      <div className="flex flex-col sm:flex-row gap-6 p-6 rounded-2xl shadow-card" style={{ backgroundColor: '#2a3142' }}>

        {/* Image Container */}
        <div className="relative flex-shrink-0">
          <div className="relative w-[170px] h-[170px] rounded-2xl overflow-hidden" style={{ backgroundColor: '#2a3142' }}>

            {/* Placeholder shown if no valid image */}
            {shouldShowPlaceholder && getPlaceholderImage(article.source_name)}

            {/* Image - Show all URLs from database */}
            {hasValidImage && (
              <img
                src={decodedImageUrl}
                alt={article.title}
                className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                onLoad={handleImageLoad}
                onError={handleImageError}
                loading="lazy"
                style={{
                  display: imageError ? 'none' : 'block'
                }}
              />
            )}

            {/* Relevance Score Badge */}
            <div className="absolute top-2 right-2 px-2 py-1 rounded-lg text-xs font-semibold z-10"
                 style={{ backgroundColor: '#1a1f2e', color: '#ffffff' }}>
              ⭐ {article.relevance_score}/5
            </div>
          </div>
        </div>

        {/* Content Container */}
        <div className="flex-1 flex flex-col justify-between min-w-0">

          {/* Top Section: Category and Date */}
          <div className="space-y-2">
            {/* Categories */}
            <div className="flex flex-wrap gap-2">
              {article.categories.slice(0, 3).map((category, index) => (
                <span
                  key={index}
                  className="inline-flex items-center text-xs font-semibold px-3 py-1 rounded-full"
                  style={{
                    backgroundColor: `${getCategoryColor(category)}20`,
                    color: getCategoryColor(category),
                    border: `1px solid ${getCategoryColor(category)}40`
                  }}
                >
                  <ChevronRight className="w-3 h-3 mr-1" />
                  {category.toUpperCase()}
                </span>
              ))}
            </div>

            {/* Date */}
            <div className="flex items-center text-sm" style={{ color: '#a0a4b8' }}>
              <Calendar className="w-4 h-4 mr-1" />
              {formatDate(article.published_date)}
              <span className="mx-2">•</span>
              <span className="text-xs">{article.source_name}</span>
            </div>
          </div>

          {/* Title */}
          <div className="mt-3">
            <h2 className="text-xl font-bold leading-tight transition-colors duration-200 group-hover:text-blue-400"
                style={{ color: '#ffffff', lineHeight: '1.4' }}>
              {article.title}
            </h2>

            {/* Accent Bar */}
            <div className="mt-2 h-1 w-12 rounded-full transition-all duration-300 group-hover:w-20"
                 style={{ backgroundColor: '#5b7fff' }} />
          </div>

          {/* Description */}
          <div className="mt-3">
            <p className="text-sm leading-relaxed line-clamp-3" style={{ color: '#a0a4b8' }}>
              {article.description}
            </p>
          </div>

          {/* Read More Link */}
          <div className="mt-4 flex items-center justify-between">
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm font-semibold transition-all duration-200 hover:translate-x-1"
              style={{ color: '#5b7fff' }}
            >
              Read More
              <ExternalLink className="w-4 h-4 ml-1" />
            </a>
          </div>
        </div>
      </div>
    </article>
  )
}