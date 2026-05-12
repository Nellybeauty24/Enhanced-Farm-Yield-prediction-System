import { motion } from 'framer-motion';

export default function SummaryCard({ label, value, unit = "", icon: Icon }) {
  return (
    <motion.div 
      whileHover={{ y: -4 }}
      className="bg-white rounded-3xl p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:shadow-emerald-500/5 transition-all"
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-gray-500 text-sm font-semibold uppercase tracking-wider">{label}</p>
          <div className="flex items-baseline gap-1">
            <h3 className="text-4xl font-bold text-gray-900 tracking-tight">
              {value}
            </h3>
            {unit && <span className="text-gray-500 font-medium">{unit}</span>}
          </div>
        </div>
        {Icon && (
          <div className="w-14 h-14 bg-emerald-50 rounded-2xl flex items-center justify-center text-emerald-600 shadow-inner">
            <Icon className="w-7 h-7" />
          </div>
        )}
      </div>
    </motion.div>
  );
}