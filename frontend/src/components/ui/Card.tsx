export function Card({
  children,
  className = '',
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-xl border border-white/5 bg-bg-surface p-4 ${className}`}>
      {children}
    </div>
  );
}
