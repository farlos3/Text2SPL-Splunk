interface SkeletonProps {
  className?: string;
  lines?: number;
}

export default function Skeleton({ className = '', lines = 1 }: SkeletonProps) {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={`h-4 bg-gray-200 dark:bg-gray-700 rounded-lg skeleton dark:skeleton-dark ${
            index < lines - 1 ? 'mb-2' : ''
          } ${index === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full'}`}
        />
      ))}
    </div>
  );
}
