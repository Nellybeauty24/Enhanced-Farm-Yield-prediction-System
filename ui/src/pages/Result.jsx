import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ResultCard from '../components/ResultCard';
import SummaryCard from '../components/SummaryCard';
import { useAuth } from '../context/AuthContext';
import { 
  TrendingUp, 
  Target, 
  Leaf, 
  BrainCircuit, 
  Zap, 
  Droplets, 
  History,
  ArrowLeft,
  LayoutDashboard,
  CheckCircle2
} from 'lucide-react';
import { motion } from 'framer-motion';
import Swal from 'sweetalert2';

export default function Result() {
  const location = useLocation();
  const { token } = useAuth();
  const navigate = useNavigate();

  // 1. ALL HOOKS MUST BE AT THE TOP
  const [profileData, setProfileData] = useState({
    state: '',
    local_gov: '',
    plot_size: '',
    longitude: '',
    latitude: ''
  });
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileMessage, setProfileMessage] = useState(null);
  const [saveErrors, setSaveErrors] = useState({});
  const [isSaved, setIsSaved] = useState(false);

  const formData = location.state?.formData;
  const prediction = location.state?.prediction;

  useEffect(() => {
    if (!formData || !prediction) {
      navigate('/input', { replace: true });
    }
  }, [formData, prediction, navigate]);

  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (!isSaved) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isSaved]);

  // 2. Early return AFTER hooks are initialized
  if (!formData || !prediction) return null;

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
    // Clear field-specific error when user starts typing
    if (saveErrors[name]) setSaveErrors(prev => ({ ...prev, [name]: null }));
  };

  const handleSaveProfile = async () => {
    setIsSavingProfile(true);
    setProfileMessage(null);
    setSaveErrors({});
    
    try {
      const payload = {
        // Geographic & operational data
        state: profileData.state,
        local_gov: profileData.local_gov,
        plot_size: parseFloat(profileData.plot_size),
        longitude: parseFloat(profileData.longitude),
        latitude: parseFloat(profileData.latitude),
        
        // Environmental data
        nitrogen: parseFloat(formData.nitrogen),
        phosphorus: parseFloat(formData.phosphorus),
        potassium: parseFloat(formData.potassium),
        ph: parseFloat(formData.ph),
        temperature: parseFloat(formData.temperature),
        rainfall: parseFloat(formData.rainfall),
        
        // Model Results
        recommended_crop: recommendedCrop,
        confidence: prediction.probability || 0.0,
        predicted_yield: yieldData ? yieldData.predicted_yield : 0.0,
        
        // High Accuracy Features
        region: formData.region,
        agro_zone: formData.agro_zone,
        soil_type: formData.soil_type,
        pest_type: formData.pest_type,
        pest_severity: formData.pest_severity,
        rainfall_variability: formData.rainfall_variability,
        labor_input: formData.labor_input
      };
      
      const response = await fetch(`/api/v1/predict/save`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify(payload)
      });
      
      const result = await response.json();
      if (!response.ok || result.status === 'error') {
        if (result.errors) {
          setSaveErrors(result.errors);
          throw new Error("Please correct the highlighted fields.");
        }
        throw new Error(result.message || 'Failed to preserve profile mapping.');
      }
      setIsSaved(true);
      setProfileMessage({ type: 'success', text: 'Farm profile successfully persisted alongside predictions!' });
    } catch (err) {
      setProfileMessage({ type: 'error', text: err.message });
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleNavigation = (e, routeTarget) => {
    e.preventDefault();
    if (isSaved) {
      navigate(routeTarget);
      return;
    }
    
    Swal.fire({
      title: 'Wait! Unsaved Data',
      text: "You haven't explicitly saved your simulation. It will be permanently lost when you navigate away.",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#059669',
      cancelButtonColor: '#ef4444',
      confirmButtonText: 'Yes, abandon data!',
      cancelButtonText: 'Cancel'
    }).then((result) => {
      if (result.isConfirmed) {
        navigate(routeTarget);
      }
    });
  };

  const [optimumData, setOptimumData] = useState(null);
  const [isFetchingOptimum, setIsFetchingOptimum] = useState(false);
  const [optimumError, setOptimumError] = useState(null);

  const fetchOptimumData = async () => {
    setIsFetchingOptimum(true);
    setOptimumError(null);
    try {
      const response = await fetch(`/api/v1/crops/${prediction.recommended_crop?.toLowerCase() || formData.crop.toLowerCase()}/requirements`);
      const result = await response.json();
      if (!response.ok || result.status === 'error') {
        throw new Error(result.message || 'Failed to fetch optimum data');
      }
      setOptimumData(result.data);
    } catch (err) {
      setOptimumError(err.message);
    } finally {
      setIsFetchingOptimum(false);
    }
  };

  const [yieldData, setYieldData] = useState(null);
  const [isFetchingYield, setIsFetchingYield] = useState(false);
  const [yieldError, setYieldError] = useState(null);

  const fetchYieldData = async () => {
    setIsFetchingYield(true);
    setYieldError(null);
    try {
      const payload = {
        crop_type: prediction.recommended_crop || formData.crop,
        nitrogen: parseFloat(formData.nitrogen),
        phosphorus: parseFloat(formData.phosphorus),
        potassium: parseFloat(formData.potassium),
        ph: parseFloat(formData.ph),
        rainfall: parseFloat(formData.rainfall),
        temperature: parseFloat(formData.temperature),
        
        // Advanced Context for CatBoost Yield Model
        region: formData.region,
        state: formData.state,
        agro_zone: formData.agro_zone,
        soil_type: formData.soil_type,
        farm_size_ha: parseFloat(formData.farm_size_ha || 1.0),
        pest_type: formData.pest_type,
        pest_severity: formData.pest_severity,
        rainfall_variability: formData.rainfall_variability,
        labor_input: formData.labor_input
      };

      const response = await fetch(`/api/v1/predict-yield`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const result = await response.json();
      if (!response.ok || result.status === 'error') {
        throw new Error(result.message || 'Failed to fetch predicted yield');
      }
      setYieldData(result.data);
    } catch (err) {
      setYieldError(err.message);
    } finally {
      setIsFetchingYield(false);
    }
  };

  const isProfileComplete = 
    profileData.state && 
    profileData.local_gov && 
    profileData.plot_size && 
    profileData.longitude && 
    profileData.latitude && 
    yieldData;

  // --- Derive display values from the real API response ---
  const recommendedCrop = prediction.recommended_crop || formData.crop;
  const confidence = prediction.probability != null
    ? Math.round(prediction.probability * 100)
    : null;
    
  const topCrops = prediction.top_recommendations || [
    { crop: recommendedCrop, probability: (confidence / 100) || 0.75 }
  ];

  // Recommendations is an array of strings from the backend
  const recommendations = prediction.recommendations || [];
  const fertilizerRec = recommendations.length > 0
    ? recommendations[0]
    : `Optimise nitrogen application for ${recommendedCrop} based on current soil readings.`;
  const irrigationRec = recommendations.length > 1
    ? recommendations[1]
    : `Based on ${formData.rainfall} mm annual rainfall, ${
    parseFloat(formData.rainfall) < 600
      ? 'supplemental irrigation is strongly recommended.'
      : parseFloat(formData.rainfall) < 1200
      ? 'moderate supplemental irrigation may be beneficial during dry spells.'
      : 'natural rainfall should be sufficient for most of the growing season.'
  }`;

  // Yield potential mapping based on confidence
  const yieldPotential = confidence != null 
    ? (confidence > 80 ? 'High' : confidence > 50 ? 'Moderate' : 'Low')
    : '—';

  const inputSummary = [
    { label: 'Nitrogen', value: formData.nitrogen, unit: 'kg/ha' },
    { label: 'Phosphorus', value: formData.phosphorus, unit: 'kg/ha' },
    { label: 'Potassium', value: formData.potassium, unit: 'kg/ha' },
    { label: 'pH', value: formData.ph, unit: '' },
    { label: 'Temperature', value: formData.temperature, unit: '°C' },
    { label: 'Rainfall', value: formData.rainfall, unit: 'mm' },
    { label: 'Selected Crop', value: formData.crop, unit: '' }
  ];

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.4 } }),
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-slate-50/50 py-16"
    >
      <div className="w-full max-w-[1600px] mx-auto px-6 lg:px-12">
        <header className="mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 border border-emerald-100 rounded-full text-emerald-700 text-sm font-semibold mb-4">
            <CheckCircle2 className="w-4 h-4" />
            Prediction complete
          </div>
          <h1 className="text-4xl font-bold text-gray-900 tracking-tight mb-2">
            Simulation Results
          </h1>
          <p className="text-gray-500 font-medium">
            Based on our advanced AI models, here is your predicted performance for{' '}
            <span className="text-emerald-700 font-bold">{formData.crop}</span>.
          </p>
        </header>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <motion.div custom={0} variants={cardVariants} initial="hidden" animate="visible">
            <SummaryCard
              label="Recommended Crop"
              value={recommendedCrop}
              icon={Leaf}
            />
          </motion.div>
          <motion.div custom={1} variants={cardVariants} initial="hidden" animate="visible">
            <SummaryCard
              label="Model Confidence"
              value={confidence != null ? confidence : '—'}
              unit={confidence != null ? '%' : ''}
              icon={Target}
            />
          </motion.div>
          <motion.div custom={2} variants={cardVariants} initial="hidden" animate="visible">
            <SummaryCard
              label="Yield Potential"
              value={yieldPotential}
              icon={TrendingUp}
            />
          </motion.div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Compatibility Ranking (Top 3) */}
          <motion.div custom={3} variants={cardVariants} initial="hidden" animate="visible">
            <ResultCard title="Compatibility Ranking (Top 3)">
              <div className="space-y-6 mb-8">
                {topCrops.map((item, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex justify-between items-end">
                      <div>
                        <span className={`text-xs font-black uppercase tracking-widest ${idx === 0 ? 'text-emerald-600' : 'text-slate-400'}`}>
                          {idx === 0 ? 'Primary Choice' : idx === 1 ? 'Strong Alternative' : 'Viable Candidate'}
                        </span>
                        <h4 className="text-xl font-bold text-slate-900">{item.crop}</h4>
                      </div>
                      <span className="text-sm font-bold text-slate-600">{Math.round(item.probability * 100)}% Match</span>
                    </div>
                    <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${item.probability * 100}%` }}
                        transition={{ duration: 1, delay: 0.5 + (idx * 0.2) }}
                        className={`h-full rounded-full ${idx === 0 ? 'bg-emerald-500' : idx === 1 ? 'bg-emerald-400' : 'bg-emerald-300'}`}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Detailed Recommendations (pH, Rainfall, etc) */}
              {recommendations.length > 2 && (
                <div className="mt-8 pt-6 border-t border-slate-100">
                  <p className="text-xs text-gray-400 font-bold uppercase tracking-widest mb-4">Optimization Advice</p>
                  <div className="space-y-3">
                    {recommendations.slice(2).map((rec, i) => (
                      <div key={i} className="flex items-start gap-3 bg-emerald-50/30 rounded-xl px-4 py-3 border border-emerald-100/20">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                        <span className="text-sm text-slate-700 leading-relaxed">{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Yield Prediction Button Section */}
              <div className="mt-8 pt-6 border-t border-slate-100 flex flex-col gap-4">
                <button 
                  onClick={fetchYieldData}
                  disabled={isFetchingYield}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-2 transition-colors disabled:opacity-50 shadow-lg shadow-emerald-200"
                >
                  {isFetchingYield ? 'Calculating Yield...' : 'Calculate Predicted Yield (kg/ha)'}
                </button>
                
                {yieldError && <p className="text-red-500 text-sm text-center font-medium">{yieldError}</p>}
                
                {yieldData && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }} 
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 bg-emerald-50 rounded-2xl border border-emerald-100 flex flex-col items-center justify-center text-center"
                  >
                    <p className="text-sm text-emerald-800 font-bold uppercase tracking-widest mb-1">Estimated Harvest Yield</p>
                    <p className="text-5xl font-black text-emerald-950 tracking-tighter shadow-sm flex items-baseline gap-2">
                      {yieldData.predicted_yield.toLocaleString(undefined, { maximumFractionDigits: 1 })}
                      <span className="text-xl font-bold text-emerald-700 lowercase">{yieldData.unit}</span>
                    </p>
                  </motion.div>
                )}
              </div>
            </ResultCard>
          </motion.div>

          {/* Strategic Recommendations */}
          <motion.div custom={4} variants={cardVariants} initial="hidden" animate="visible">
            <ResultCard title="Strategic Recommendations">
              <div className="space-y-6">
                <div className="flex gap-6 items-start">
                  <div className="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center flex-shrink-0 text-emerald-700">
                    <Zap className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900 text-lg mb-1">Fertilizer Strategy</h4>
                    <p className="text-gray-600 text-sm leading-relaxed">{fertilizerRec}</p>
                  </div>
                </div>

                <div className="flex gap-6 items-start">
                  <div className="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center flex-shrink-0 text-blue-700">
                    <Droplets className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900 text-lg mb-1">Irrigation Schedule</h4>
                    <p className="text-gray-600 text-sm leading-relaxed">{irrigationRec}</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <button 
                    onClick={fetchOptimumData}
                    disabled={isFetchingOptimum}
                    className="w-full bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold py-4 rounded-2xl flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
                  >
                    {isFetchingOptimum ? 'Fetching...' : 'View Optimum Crop Requirements'}
                  </button>

                  {optimumError && (
                    <p className="text-red-500 text-sm mt-4 text-center font-medium">{optimumError}</p>
                  )}
                  
                  {optimumData && (
                    <motion.div 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="mt-6 bg-slate-50 flex flex-col rounded-2xl p-6 border border-slate-200 shadow-inner"
                    >
                      <h4 className="font-bold text-gray-900 mb-2 capitalize text-lg">{optimumData.crop} Optimal Ranges</h4>
                      <p className="text-sm text-gray-600 mb-6">{optimumData.description}</p>
                      
                      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                        {Object.entries(optimumData.requirements).map(([key, range]) => (
                          <div key={key} className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between">
                            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-2">{key.replace('_', ' ')}</span>
                            <span className="text-xl font-black text-gray-900 tracking-tight">{range[0]} - {range[1]}</span>
                            {optimumData.units && optimumData.units[key] && (
                              <span className="block text-[10px] text-gray-400 mt-2 leading-tight uppercase font-bold tracking-wide">{optimumData.units[key]}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </div>
              </div>
            </ResultCard>
          </motion.div>
        </div>

        {/* Input Summary */}
        <motion.div custom={5} variants={cardVariants} initial="hidden" animate="visible">
          <ResultCard title="Input Summary" className="!p-10">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-8">
              {inputSummary.map((item, index) => (
                <div key={index} className="group">
                  <p className="text-xs text-gray-400 font-bold uppercase tracking-widest mb-2 group-hover:text-emerald-600 transition-colors leading-tight">{item.label}</p>
                  <div className="flex items-baseline gap-1">
                    <p className="text-xl font-bold text-gray-900">{item.value}</p>
                    {item.unit && <span className="text-xs text-gray-500 font-medium">{item.unit}</span>}
                  </div>
                </div>
              ))}
            </div>
          </ResultCard>
        </motion.div>

        {/* Farm Profile Persistence Form */}
        <motion.div custom={6} variants={cardVariants} initial="hidden" animate="visible" className="mt-8">
          <ResultCard title="Farm Profile Data" className="!p-8 bg-white border border-slate-200">
            <h4 className="text-gray-500 text-sm mb-6 font-medium">Please enter your geographical data to officially commit the simulation to your operational records.</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">State</label>
                <input type="text" name="state" value={profileData.state} onChange={handleProfileChange} className={`w-full bg-slate-50 border-2 ${saveErrors.state ? 'border-red-500' : 'border-slate-100'} px-4 py-3 rounded-xl outline-none focus:bg-white focus:border-emerald-500 transition-all font-medium`} placeholder="E.g., Lagos" />
                {saveErrors.state && <span className="text-red-500 text-[10px] font-bold uppercase tracking-widest pl-2 mt-1 block">{Array.isArray(saveErrors.state) ? saveErrors.state[0] : saveErrors.state}</span>}
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Local Government Area</label>
                <input type="text" name="local_gov" value={profileData.local_gov} onChange={handleProfileChange} className={`w-full bg-slate-50 border-2 ${saveErrors.local_gov ? 'border-red-500' : 'border-slate-100'} px-4 py-3 rounded-xl outline-none focus:bg-white focus:border-emerald-500 transition-all font-medium`} placeholder="E.g., Ikeja" />
                {saveErrors.local_gov && <span className="text-red-500 text-[10px] font-bold uppercase tracking-widest pl-2 mt-1 block">{Array.isArray(saveErrors.local_gov) ? saveErrors.local_gov[0] : saveErrors.local_gov}</span>}
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Plot Size (ha)</label>
                <input type="number" step="0.1" name="plot_size" value={profileData.plot_size} onChange={handleProfileChange} className={`w-full bg-slate-50 border-2 ${saveErrors.plot_size ? 'border-red-500' : 'border-slate-100'} px-4 py-3 rounded-xl outline-none focus:bg-white focus:border-emerald-500 transition-all font-medium`} placeholder="0.0" />
                {saveErrors.plot_size && <span className="text-red-500 text-[10px] font-bold uppercase tracking-widest pl-2 mt-1 block">{Array.isArray(saveErrors.plot_size) ? saveErrors.plot_size[0] : saveErrors.plot_size}</span>}
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Longitude</label>
                <input type="number" step="0.000001" name="longitude" value={profileData.longitude} onChange={handleProfileChange} className={`w-full bg-slate-50 border-2 ${saveErrors.longitude ? 'border-red-500' : 'border-slate-100'} px-4 py-3 rounded-xl outline-none focus:bg-white focus:border-emerald-500 transition-all font-medium`} placeholder="e.g. 3.4064" />
                {saveErrors.longitude && <span className="text-red-500 text-[10px] font-bold uppercase tracking-widest pl-2 mt-1 block">{Array.isArray(saveErrors.longitude) ? saveErrors.longitude[0] : saveErrors.longitude}</span>}
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Latitude</label>
                <input type="number" step="0.000001" name="latitude" value={profileData.latitude} onChange={handleProfileChange} className={`w-full bg-slate-50 border-2 ${saveErrors.latitude ? 'border-red-500' : 'border-slate-100'} px-4 py-3 rounded-xl outline-none focus:bg-white focus:border-emerald-500 transition-all font-medium`} placeholder="e.g. 6.4541" />
                {saveErrors.latitude && <span className="text-red-500 text-[10px] font-bold uppercase tracking-widest pl-2 mt-1 block">{Array.isArray(saveErrors.latitude) ? saveErrors.latitude[0] : saveErrors.latitude}</span>}
              </div>
            </div>

            <button 
              onClick={handleSaveProfile}
              disabled={!isProfileComplete || isSavingProfile || isSaved}
              className={`w-full font-bold py-5 rounded-2xl flex items-center justify-center gap-2 shadow-xl transition-all focus:ring ${
                isSaved 
                  ? 'bg-slate-100 text-emerald-700 border-2 border-emerald-100 cursor-default shadow-none' 
                  : 'bg-emerald-900 border border-emerald-800 text-white hover:bg-emerald-800 shadow-emerald-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isSaved ? (
                <>
                  <CheckCircle2 className="w-5 h-5" />
                  Simulation Saved to History
                </>
              ) : isSavingProfile ? (
                'Saving Data...'
              ) : (
                yieldData ? 'Save Complete Prediction Data' : 'Waiting for Yield Calculation...'
              )}
            </button>
            {profileMessage && (
              <p className={`mt-4 text-center font-bold text-sm ${profileMessage.type === 'error' ? 'text-red-500' : 'text-emerald-600'}`}>{profileMessage.text}</p>
            )}
          </ResultCard>
        </motion.div>

        <div className="mt-12 flex flex-col sm:flex-row gap-6">
          <button
            onClick={(e) => handleNavigation(e, '/input')}
            className="flex-1 flex items-center justify-center gap-2 bg-white text-gray-900 border-2 border-slate-100 font-bold py-5 rounded-[2rem] transition-all hover:bg-slate-50 hover:border-slate-200 active:scale-95"
          >
            <History className="w-5 h-5" />
            New Simulation
          </button>
          <button
            onClick={(e) => handleNavigation(e, '/dashboard')}
            className="flex-1 flex items-center justify-center gap-2 bg-emerald-900 text-white font-bold py-5 rounded-[2rem] shadow-xl shadow-emerald-200 transition-all hover:bg-emerald-950 active:scale-95"
          >
            <LayoutDashboard className="w-5 h-5" />
            View Advanced Analytics
          </button>
        </div>
      </div>
    </motion.div>
  );
}