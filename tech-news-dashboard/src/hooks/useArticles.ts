import { useState, useEffect, useMemo } from 'react'
import { supabase, Article, Category } from '@/lib/supabase'

export function useArticles() {
  const [articles, setArticles] = useState<Article[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [sortBy, setSortBy] = useState<'recent' | 'relevance'>('recent')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const [allArticles, setAllArticles] = useState<Article[]>([])

  const itemsPerPage = 12

  // Fetch categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const { data, error } = await supabase
          .from('categories')
          .select(`
            id,
            name,
            article_categories(count)
          `)
          .order('name')

        if (error) throw error

        const formattedCategories: Category[] = data.map((cat: any) => ({
          id: cat.id,
          name: cat.name,
          article_count: cat.article_categories?.length || 0
        }))

        setCategories(formattedCategories)
      } catch (err) {
        console.error('Error fetching categories:', err)
      }
    }

    fetchCategories()
  }, [])

  // Fetch all articles
  const fetchAllArticles = async () => {
    setLoading(true)
    setError(null)

    try {
      let query = supabase
        .from('articles')
        .select(`
          id,
          title,
          description,
          url,
          image_url,
          published_date,
          relevance_score,
          created_at,
          sources!inner(name),
          article_categories (
            categories!inner(name)
          )
        `)
        .eq('filtered', false)

      // Apply search filter
      if (searchQuery.trim()) {
        query = query.or(
          `title.ilike.%${searchQuery}%,description.ilike.%${searchQuery}%`
        )
      }

      // Apply sorting
      if (sortBy === 'recent') {
        query = query.order('published_date', { ascending: false })
      } else {
        query = query.order('relevance_score', { ascending: false })
      }

      const { data, error } = await query

      if (error) throw error

      const formattedArticles: Article[] = data.map((article: any) => ({
        id: article.id,
        title: article.title,
        description: article.description || 'No description available',
        url: article.url,
        image_url: article.image_url || '',
        published_date: article.published_date,
        relevance_score: article.relevance_score || 3,
        source_name: article.sources?.name || 'Unknown',
        categories: article.article_categories?.map((ac: any) => ac.categories?.name).filter(Boolean) || []
      }))

      setAllArticles(formattedArticles)
      setTotalItems(formattedArticles.length)
    } catch (err) {
      console.error('Error fetching articles:', err)
      setError('Failed to load articles. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Initial fetch
  useEffect(() => {
    fetchAllArticles()
  }, [searchQuery, sortBy])

  // Filter articles based on selected categories
  const filteredArticles = useMemo(() => {
    if (selectedCategories.length === 0) {
      return allArticles
    }

    return allArticles.filter(article => {
      // Check if article has any of the selected categories
      return selectedCategories.some(selectedCategory =>
        article.categories.includes(selectedCategory)
      )
    })
  }, [allArticles, selectedCategories])

  // Update total items when filtered articles change
  useEffect(() => {
    setTotalItems(filteredArticles.length)
    setCurrentPage(1) // Reset to first page when filters change
  }, [filteredArticles])

  // Get current page articles
  const paginatedArticles = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    return filteredArticles.slice(startIndex, endIndex)
  }, [filteredArticles, currentPage, itemsPerPage])

  const totalPages = Math.ceil(totalItems / itemsPerPage)

  const handleSearch = (query: string) => {
    setSearchQuery(query)
  }

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    )
  }

  const handleClearFilters = () => {
    setSelectedCategories([])
    setSearchQuery('')
  }

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

  return {
    articles: paginatedArticles,
    allArticlesCount: allArticles.length,
    filteredArticlesCount: filteredArticles.length,
    categories,
    loading,
    error,
    searchQuery,
    selectedCategories,
    sortBy,
    currentPage,
    totalPages,
    totalItems,
    itemsPerPage,
    handleSearch,
    handleCategoryToggle,
    handleClearFilters,
    handlePageChange,
    refetch: fetchAllArticles,
    setSortBy
  }
}