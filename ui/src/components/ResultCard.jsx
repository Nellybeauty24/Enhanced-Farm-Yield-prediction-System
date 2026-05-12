export default function ResultCard({ title, children, className = "" }) {
  return (
    <div className={`bg-white rounded-[2.5rem] border border-gray-100 p-8 sm:p-12 shadow-sm ${className}`}>
      {title && <h2 className="text-2xl font-bold text-gray-900 mb-8 tracking-tight">{title}</h2>}
      {children}
    </div>
  );
}