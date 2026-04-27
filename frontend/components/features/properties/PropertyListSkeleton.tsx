export function PropertyListSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div 
          key={i} 
          className="flex flex-col overflow-hidden rounded-lg border border-slate-200 bg-white"
        >
          <div className="aspect-[16/9] w-full animate-pulse bg-slate-200" />
          <div className="flex flex-1 flex-col p-4">
            <div className="mb-4 space-y-2">
              <div className="h-5 w-3/4 animate-pulse rounded bg-slate-200" />
              <div className="h-4 w-1/2 animate-pulse rounded bg-slate-200" />
            </div>
            <div className="mt-auto space-y-4">
              <div className="h-7 w-1/3 animate-pulse rounded bg-slate-200" />
              <div className="flex gap-3 border-t border-slate-100 pt-3">
                <div className="h-4 w-12 animate-pulse rounded bg-slate-200" />
                <div className="h-4 w-12 animate-pulse rounded bg-slate-200" />
                <div className="h-4 w-12 animate-pulse rounded bg-slate-200" />
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
