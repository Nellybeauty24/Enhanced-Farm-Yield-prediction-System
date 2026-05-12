export default function ChartSection({ title, children }) {
  return (
    <div className="bg-white rounded-[2rem] p-8 border border-gray-100 shadow-sm">
      <h3 className="text-xl font-bold text-gray-900 mb-8 tracking-tight">{title}</h3>
      <div className="w-full">
        {children}
      </div>
    </div>
  );
}