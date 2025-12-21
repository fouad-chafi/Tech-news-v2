export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        <div className="w-12 h-12 rounded-full border-4 border-gray-700 border-t-blue-500 animate-spin"></div>
        <div className="absolute inset-0 w-12 h-12 rounded-full border-4 border-transparent border-r-blue-400 animate-spin animation-delay-150"></div>
      </div>
      <p className="mt-4 text-sm" style={{ color: '#a0a4b8' }}>
        Loading latest articles...
      </p>
    </div>
  )
}