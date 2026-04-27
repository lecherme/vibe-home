export function PropertyListSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <div 
          key={i} 
          className="bg-white rounded-lg border border-slate-200 overflow-hidden"
        >
          <div className="aspect-[4/3] bg-slate-100 animate-pulse" />
          <div className="p-4 space-y-4">
            <div className="flex justify-between items-start">
              <div className="h-6 bg-slate-100 rounded w-2/3 animate-pulse" />
              <div className="h-6 bg-slate-100 rounded w-1/4 animate-pulse" />
            </div>
            <div className="h-4 bg-slate-100 rounded w-1/2 animate-pulse" />
            <div className="flex gap-4">
              <div className="h-4 bg-slate-100 rounded w-12 animate-pulse" />
              <div className="h-4 bg-slate-100 rounded w-12 animate-pulse" />
              <div className="h-4 bg-slate-100 rounded w-12 animate-pulse" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
