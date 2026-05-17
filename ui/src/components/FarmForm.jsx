import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Beaker,
  Thermometer,
  CloudRain,
  Database,
  FlaskConical,
  Droplets,
  MapPin,
  Mountain,
  Bug,
  Scaling,
  Users,
  ChevronDown,
  ChevronUp,
  Settings2,
  ChevronRight,
  Wind
} from 'lucide-react';

export default function FarmForm({ onSubmit, isLoading = false, errors: externalErrors = {} }) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    ph: '',
    temperature: '',
    rainfall: '',
    humidity: '',
    // New Advanced Fields
    region: 'None',
    state: 'None',
    agro_zone: 'Derived Savanna',
    soil_type: 'Loamy'
  });

  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    const requiredNumeric = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature', 'rainfall', 'humidity'];
    requiredNumeric.forEach(field => {
      if (!formData[field] || isNaN(formData[field])) newErrors[field] = 'Required';
    });

    if (parseFloat(formData.ph) < 0 || parseFloat(formData.ph) > 14) newErrors.ph = '0-14';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) onSubmit(formData);
  };

  const coreFields = [
    { name: 'nitrogen',   label: 'Nitrogen (N)',   icon: <FlaskConical className="w-5 h-5" /> },
    { name: 'phosphorus', label: 'Phosphorus (P)', icon: <Beaker className="w-5 h-5" /> },
    { name: 'potassium',  label: 'Potassium (K)',  icon: <Database className="w-5 h-5" /> },
    { name: 'ph',         label: 'Soil pH',        icon: <Droplets className="w-5 h-5" /> },
    { name: 'temperature',label: 'Temp (°C)',      icon: <Thermometer className="w-5 h-5" /> },
    { name: 'rainfall',   label: 'Rainfall (mm)',  icon: <CloudRain className="w-5 h-5" /> },
    { name: 'humidity',   label: 'Humidity (%)',   icon: <Wind className="w-5 h-5" /> }
  ];

  const advancedFields = [
    { name: 'region', label: 'Region', icon: <MapPin className="w-5 h-5" />, type: 'select', options: ['None', 'Northcentral', 'Northeast', 'Northwest', 'Southeast', 'Southsouth', 'Southwest'] },
    { name: 'state', label: 'State', icon: <MapPin className="w-5 h-5" />, type: 'select', options: ['None', 'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'] },
    { name: 'agro_zone', label: 'Agro Zone', icon: <Mountain className="w-5 h-5" />, type: 'select', options: ['Derived Savanna', 'Humid Forest', 'Northern Guinea Savanna', 'Sahel Savanna', 'Sudan Savanna'] },
    { name: 'soil_type', label: 'Soil Type', icon: <Droplets className="w-5 h-5" />, type: 'select', options: ['Clayey', 'Lateritic', 'Loamy', 'Sandy'] }
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Core Parameters Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {coreFields.map((field, index) => (
          <InputField 
            key={field.name} 
            field={field} 
            value={formData[field.name]} 
            error={errors[field.name] || (externalErrors[field.name] ? (Array.isArray(externalErrors[field.name]) ? externalErrors[field.name][0] : externalErrors[field.name]) : null)} 
            onChange={handleChange}
            index={index}
          />
        ))}
      </div>

      {/* Advanced Parameters Toggle */}
      <div className="pt-4 border-t border-slate-100">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-emerald-600 transition-colors"
        >
          <Settings2 className="w-5 h-5" />
          Advanced Regional & Operational Parameters
          {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        <AnimatePresence>
          {showAdvanced && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-6 pb-2">
                {advancedFields.map((field, index) => (
                  <div key={field.name} className="space-y-2">
                    <label className="flex items-center gap-2 text-sm font-bold text-gray-700 ml-1">
                      <span className="text-slate-400">{field.icon}</span>
                      {field.label}
                    </label>
                    {field.type === 'select' ? (
                      <select
                        name={field.name}
                        value={formData[field.name]}
                        onChange={handleChange}
                        className={`w-full bg-slate-50 border-2 ${errors[field.name] || externalErrors[field.name] ? 'border-red-500' : 'border-slate-100'} px-4 py-3 rounded-2xl outline-none transition-all focus:bg-white focus:border-emerald-500 appearance-none text-sm font-medium`}
                      >
                        {field.options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                      </select>
                    ) : (
                      <input
                        type="number"
                        name={field.name}
                        value={formData[field.name]}
                        onChange={handleChange}
                        step="0.1"
                        className={`w-full bg-slate-50 border-2 ${errors[field.name] || externalErrors[field.name] ? 'border-red-500' : 'border-slate-100'} px-4 py-3 rounded-2xl outline-none transition-all focus:bg-white focus:border-emerald-500 text-sm font-medium`}
                      />
                    )}
                    {(errors[field.name] || externalErrors[field.name]) && (
                      <span className="text-red-500 text-[10px] font-bold uppercase tracking-wider pl-2 mt-1 block">
                        {errors[field.name] || (Array.isArray(externalErrors[field.name]) ? externalErrors[field.name][0] : externalErrors[field.name])}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <motion.button
        type="submit"
        disabled={isLoading}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.98 }}
        className="group relative w-full bg-emerald-600 disabled:bg-slate-300 text-white font-bold py-5 rounded-[1.5rem] flex items-center justify-center gap-3 shadow-xl shadow-emerald-200 transition-all hover:bg-emerald-700"
      >
        {isLoading ? (
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Generating Deep Insight...
          </div>
        ) : (
          <>
            Calculate High-Accuracy Prediction
            <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </>
        )}
      </motion.button>
    </form>
  );
}

function InputField({ field, value, error, onChange, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="space-y-2"
    >
      <label className="flex items-center gap-2 text-sm font-bold text-gray-700 ml-1">
        <span className="text-emerald-600">{field.icon}</span>
        {field.label}
      </label>
      <div className="relative group">
        <input
          type="number"
          name={field.name}
          value={value}
          onChange={onChange}
          step="0.1"
          placeholder="0.0"
          className={`w-full bg-slate-50 border-2 px-4 py-4 rounded-2xl outline-none transition-all focus:bg-white focus:shadow-lg focus:shadow-emerald-500/5 font-medium ${
            error
              ? 'border-red-500 focus:border-red-600'
              : 'border-slate-100 focus:border-emerald-500'
          }`}
        />
      </div>
      {error && (
        <span className="text-red-500 text-[10px] font-bold uppercase tracking-widest pl-2 mt-1 block">
          {error}
        </span>
      )}
    </motion.div>
  );
}