import { useState, useEffect } from 'react';
import SummaryCard from '../components/SummaryCard';
import { 
  TrendingUp, 
  Award, 
  Info, 
  RefreshCw, 
  Loader, 
  AlertTriangle, 
  MapPin, 
  ChevronRight, 
  X, 
  Save,
  CheckCircle2,
  Calendar
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

const API_BASE = '/api/v1';

const fetchWithFallback = async (url, token) => {
  const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
};

export default function Dashboard() {
  const { token, user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);
  const [filterCrop, setFilterCrop] = useState('');

  // Modal State
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [actualYieldInput, setActualYieldInput] = useState('');
  const [isUpdatingYield, setIsUpdatingYield] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const summaryUrl = `${API_BASE}/analytics/summary${filterCrop ? `?crop=${encodeURIComponent(filterCrop)}` : ''}`;
      const [summaryRes, historyRes] = await Promise.all([
        fetchWithFallback(summaryUrl, token),
        fetchWithFallback(`${API_BASE}/analytics/history-records`, token),
      ]);

      setSummary(summaryRes.data);
      setRecords(historyRes.data || []);
      setLastRefreshed(new Date());
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError('Failed to load dashboard data. Ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filterCrop]);

  const availableCrops = Array.from(new Set(records.map(r => r.recommended_crop))).sort();

  const handleUpdateYield = async () => {
    if (!actualYieldInput || isNaN(actualYieldInput)) {
      Swal.fire('Invalid Input', 'Please enter a valid numeric yield value.', 'error');
      return;
    }

    setIsUpdatingYield(true);
    try {
      const response = await fetch(`${API_BASE}/predict/${selectedRecord.id}/actual-yield`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ actual_yield: parseFloat(actualYieldInput) })
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Failed to update harvest yield');

      Swal.fire({
        title: 'Success!',
        text: 'Harvest yield explicitly updated in operations!',
        icon: 'success',
        confirmButtonColor: '#059669'
      });

      // Update local state gracefully so we don't need a full explicit reload
      setRecords(prev => prev.map(rec => 
        rec.id === selectedRecord.id 
          ? { ...rec, actual_yield: parseFloat(actualYieldInput) } 
          : rec
      ));
      
      setSelectedRecord(prev => ({...prev, actual_yield: parseFloat(actualYieldInput)}));
      setActualYieldInput('');

    } catch (err) {
      Swal.fire('Error', err.message, 'error');
    } finally {
      setIsUpdatingYield(false);
    }
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.4 } }),
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-slate-50/50 py-12 relative"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <header className="mb-12 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight mb-2">
              Historical Log Book
            </h1>
            <p className="text-gray-500 font-medium">
              Browse your specifically persisted simulation records.
            </p>
            {lastRefreshed && !loading && (
              <p className="text-xs text-gray-400 mt-1">
                Last synchronized: {lastRefreshed.toLocaleTimeString()}
              </p>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-4 mt-1">
            <div className="relative">
              <select
                value={filterCrop}
                onChange={(e) => setFilterCrop(e.target.value)}
                className="appearance-none bg-white border border-gray-200 text-gray-700 font-bold py-3 pl-5 pr-12 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all shadow-sm cursor-pointer"
              >
                <option value="">All Crops Performance</option>
                {availableCrops.map(crop => (
                  <option key={crop} value={crop}>{crop} Specifics</option>
                ))}
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                <ChevronRight className="w-5 h-5 rotate-90" />
              </div>
            </div>
            
            <button
              onClick={loadData}
              disabled={loading}
              className="flex items-center justify-center gap-2 px-6 py-3 rounded-2xl bg-white border border-gray-200 text-gray-600 font-bold hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 transition-all disabled:opacity-50 active:scale-95 shadow-sm"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Sync Records
            </button>
          </div>
        </header>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8 p-5 rounded-2xl bg-red-50 border border-red-100 text-red-700 text-sm flex items-center gap-3"
            >
              <AlertTriangle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {loading && !summary ? (
          <div className="flex flex-col items-center justify-center py-32 gap-4 text-emerald-600">
            <Loader className="w-12 h-12 animate-spin" />
            <p className="font-bold text-lg tracking-tight">Decoupling Datastreams...</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
              <motion.div custom={0} variants={cardVariants} initial="hidden" animate="visible">
                <SummaryCard
                  label="Average Expected Yield"
                  value={summary ? `${(summary.avg_yield || 0).toLocaleString()}` : '—'}
                  unit="kg/ha"
                  icon={TrendingUp}
                />
              </motion.div>
              <motion.div custom={1} variants={cardVariants} initial="hidden" animate="visible">
                <SummaryCard
                  label="Yield Performance Gap"
                  value={summary ? (summary.avg_actual > 0 ? (summary.yield_diff > 0 ? `+${summary.yield_diff.toLocaleString()}` : summary.yield_diff.toLocaleString()) : 'Pending') : '—'}
                  unit={summary?.avg_actual > 0 ? "kg/ha" : ""}
                  icon={Award}
                />
              </motion.div>
              <motion.div custom={2} variants={cardVariants} initial="hidden" animate="visible">
                <SummaryCard
                  label="Common Farm Crop"
                  value={summary?.top_crop || '—'}
                  icon={Info}
                />
              </motion.div>
              <motion.div custom={3} variants={cardVariants} initial="hidden" animate="visible">
                <SummaryCard
                  label="Total Simulations"
                  value={records.length.toLocaleString()}
                  unit="records"
                  icon={CheckCircle2}
                />
              </motion.div>
            </div>

      {/* Main History Table/List */}
      <motion.div custom={3} variants={cardVariants} initial="hidden" animate="visible" className="bg-white rounded-[2rem] border border-gray-100 shadow-sm overflow-hidden p-2">
        <div className="p-6 border-b border-gray-50 flex items-center justify-between">
          <h3 className="font-bold text-gray-900 text-xl tracking-tight">
            {filterCrop ? `${filterCrop} Simulation History` : 'Farm Simulation History'}
          </h3>
          <span className="text-xs font-bold bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full">
            {filterCrop ? records.filter(r => r.recommended_crop === filterCrop).length : records.length} total
          </span>
        </div>
        
        {records.length === 0 ? (
          <div className="p-16 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
              <Info className="w-8 h-8 text-gray-300" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">No Records Found</h3>
            <p className="text-gray-500 max-w-sm">You haven't explicitly saved any farm simulations to your account yet. Navigate to the Predict tool to get started!</p>
          </div>
        ) : records.filter(r => !filterCrop || r.recommended_crop === filterCrop).length === 0 ? (
          <div className="p-16 flex flex-col items-center justify-center text-center">
            <h3 className="text-xl font-bold text-gray-900 mb-2">No {filterCrop} Records</h3>
            <p className="text-gray-500 max-w-sm">You haven't saved any simulations for this specific crop yet.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {records
              .filter(record => !filterCrop || record.recommended_crop === filterCrop)
              .map((record) => (
              <div key={record.id} className="p-6 flex flex-col xl:flex-row xl:items-center justify-between gap-6 hover:bg-slate-50 transition-colors">
                      {/* Meta Profile */}
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center flex-shrink-0">
                          <CheckCircle2 className="w-6 h-6 text-emerald-700" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="text-lg font-bold text-gray-900">{record.recommended_crop}</h4>
                            <span className="text-xs font-bold text-gray-400 bg-gray-100 px-2 py-0.5 rounded-md flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {new Date(record.timestamp).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-gray-500 font-medium">
                            <MapPin className="w-4 h-4 text-emerald-600" />
                            {record.local_gov}, {record.state} • {record.plot_size} hectares
                          </div>
                        </div>
                      </div>

                      {/* Yield Comparisons */}
                      <div className="flex items-center gap-8 bg-white border border-gray-100 rounded-2xl p-4 shadow-sm w-full xl:w-auto">
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Expected Yield</span>
                          <span className="text-lg font-black text-gray-900 tracking-tight">{(record.predicted_yield || 0).toLocaleString()} <span className="text-sm text-gray-400 font-medium lowercase">kg/ha</span></span>
                        </div>
                        <div className="w-px h-10 bg-gray-100"></div>
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Actual Yield</span>
                          {record.actual_yield ? (
                            <span className="text-lg font-black text-emerald-600 tracking-tight">{(record.actual_yield).toLocaleString()} <span className="text-sm text-emerald-600/70 font-medium lowercase">kg/ha</span></span>
                          ) : (
                            <span className="text-sm font-medium text-amber-500 flex items-center gap-1">No Data <AlertTriangle className="w-4 h-4" /></span>
                          )}
                        </div>
                      </div>

                      <button 
                        onClick={() => { setSelectedRecord(record); setActualYieldInput(''); }}
                        className="bg-gray-900 hover:bg-emerald-700 text-white font-bold py-3 px-6 rounded-xl flex items-center justify-center gap-2 transition-colors flex-shrink-0"
                      >
                        View Details
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </>
        )}
      </div>

      {/* Details Modal */}
      <AnimatePresence>
        {selectedRecord && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
            {/* Backdrop */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedRecord(null)}
              className="fixed inset-0 bg-gray-900/40 backdrop-blur-sm"
            />
            
            {/* Modal Content */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative bg-white rounded-[2rem] shadow-2xl w-full max-w-4xl overflow-hidden flex flex-col max-h-[90vh]"
            >
              {/* Header */}
              <div className="bg-emerald-900 p-6 flex items-center justify-between sticky top-0 z-10">
                <div className="flex items-center gap-4 text-white">
                  <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center text-emerald-300">
                    <CheckCircle2 />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold tracking-tight">Simulation Overview</h3>
                    <p className="text-emerald-200 text-sm font-medium">Record ID: #{selectedRecord.id} • Saved on {new Date(selectedRecord.timestamp).toLocaleString()}</p>
                  </div>
                </div>
                <button 
                  onClick={() => setSelectedRecord(null)}
                  className="p-2 bg-white/10 hover:bg-white/20 rounded-full text-white transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Scrollable Body */}
              <div className="flex-1 overflow-y-auto p-8 bg-slate-50">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  
                  {/* Left Column: Environmental Inputs */}
                  <div className="space-y-6">
                    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                      <h4 className="font-bold text-gray-900 mb-6 flex items-center gap-2"><MapPin className="w-5 h-5 text-emerald-600" /> Geography Details</h4>
                      <div className="grid grid-cols-2 gap-y-4 gap-x-2 text-sm">
                        <div className="flex flex-col"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">State</span><span className="font-medium text-gray-900">{selectedRecord.state}</span></div>
                        <div className="flex flex-col"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">L.G.A</span><span className="font-medium text-gray-900">{selectedRecord.local_gov}</span></div>
                        <div className="flex flex-col"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Latitude</span><span className="font-medium text-gray-900">{selectedRecord.latitude}</span></div>
                        <div className="flex flex-col"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Longitude</span><span className="font-medium text-gray-900">{selectedRecord.longitude}</span></div>
                        <div className="flex flex-col col-span-2"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Plot Dimensions</span><span className="font-bold text-emerald-700">{selectedRecord.plot_size} Hectares</span></div>
                      </div>
                    </div>

                    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                      <h4 className="font-bold text-gray-900 mb-6 flex items-center gap-2"><TrendingUp className="w-5 h-5 text-blue-600" /> Environmental Parameters</h4>
                      <div className="grid grid-cols-2 gap-y-6 text-sm">
                        <div className="flex flex-col gap-1"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Nitrogen (N)</span><span className="font-black text-gray-900 text-lg">{selectedRecord.nitrogen}<span className="text-xs font-medium text-gray-500 ml-1">kg/ha</span></span></div>
                        <div className="flex flex-col gap-1"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Phosphorus (P)</span><span className="font-black text-gray-900 text-lg">{selectedRecord.phosphorus}<span className="text-xs font-medium text-gray-500 ml-1">kg/ha</span></span></div>
                        <div className="flex flex-col gap-1"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Potassium (K)</span><span className="font-black text-gray-900 text-lg">{selectedRecord.potassium}<span className="text-xs font-medium text-gray-500 ml-1">kg/ha</span></span></div>
                        <div className="flex flex-col gap-1"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Soil pH Level</span><span className="font-black text-gray-900 text-lg">{selectedRecord.ph}</span></div>
                        <div className="flex flex-col gap-1"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Temperature</span><span className="font-black text-gray-900 text-lg">{selectedRecord.temperature}<span className="text-xs font-medium text-gray-500 ml-1">°C</span></span></div>
                        <div className="flex flex-col gap-1"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Annual Rainfall</span><span className="font-black text-gray-900 text-lg">{selectedRecord.rainfall}<span className="text-xs font-medium text-gray-500 ml-1">mm</span></span></div>
                        <div className="flex flex-col gap-1"><span className="text-gray-400 font-bold uppercase text-[10px] tracking-wider">Humidity</span><span className="font-black text-gray-900 text-lg">{selectedRecord.humidity}<span className="text-xs font-medium text-gray-500 ml-1">%</span></span></div>
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Model Output & Harvest Updates */}
                  <div className="space-y-6">
                    <div className="bg-gradient-to-br from-emerald-600 to-emerald-800 p-8 rounded-2xl shadow-md text-white">
                      <p className="text-emerald-200 font-bold uppercase tracking-widest text-xs mb-2">Model Recommendation</p>
                      <h4 className="text-4xl font-black mb-6 drop-shadow-md">{selectedRecord.recommended_crop}</h4>
                      <div className="grid grid-cols-2 gap-4">
                         <div className="bg-white/10 rounded-xl p-4 border border-white/20">
                            <span className="block text-emerald-200 text-xs font-bold uppercase tracking-wider mb-1">Confidence</span>
                            <span className="text-2xl font-black">
                               {selectedRecord.confidence > 1 
                                 ? Math.round(selectedRecord.confidence) 
                                 : Math.round(selectedRecord.confidence * 100)}%
                            </span>
                         </div>
                         <div className="bg-white/10 rounded-xl p-4 border border-white/20">
                            <span className="block text-emerald-200 text-xs font-bold uppercase tracking-wider mb-1">Expected Yield</span>
                            <span className="text-2xl font-black">{(selectedRecord.predicted_yield || 0).toLocaleString()} <span className="text-sm font-medium text-emerald-100">kg/ha</span></span>
                         </div>
                      </div>
                    </div>

                    <div className="bg-amber-50 p-6 rounded-2xl border border-amber-200 shadow-sm relative overflow-hidden">
                      <div className="absolute -right-4 -bottom-4 text-amber-200 opacity-50">
                        <Award className="w-32 h-32" />
                      </div>
                      <h4 className="font-bold text-amber-900 mb-2 relative z-10">Post-Harvest Update</h4>
                      <p className="text-sm text-amber-800 mb-6 relative z-10">Log your real-world crop yield (kg/ha) to close the intelligence loop on this model simulation.</p>
                      
                      <div className="relative z-10 flex gap-3">
                        <div className="flex-1">
                          <input 
                            type="number" 
                            step="0.01"
                            placeholder={selectedRecord.actual_yield ? `Current: ${selectedRecord.actual_yield} kg/ha` : "Enter actual yield (kg/ha)"}
                            value={actualYieldInput}
                            onChange={(e) => setActualYieldInput(e.target.value)}
                            className="w-full bg-white border-2 border-amber-100 px-4 py-3 rounded-xl outline-none focus:border-amber-500 font-bold text-gray-900 placeholder-amber-400"
                          />
                        </div>
                        <button 
                          onClick={handleUpdateYield}
                          disabled={isUpdatingYield || !actualYieldInput}
                          className="bg-amber-500 hover:bg-amber-600 active:bg-amber-700 text-white font-bold py-3 px-6 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-amber-200 flex items-center gap-2 shrink-0"
                        >
                          {isUpdatingYield ? 'Saving...' : <><Save className="w-5 h-5"/> Commit</>}
                        </button>
                      </div>
                      {selectedRecord.actual_yield && !actualYieldInput && (
                        <p className="text-amber-700 text-xs font-bold mt-4 flex items-center gap-1 z-10 relative">
                          <CheckCircle2 className="w-4 h-4"/> Harvest logged successfully. Model closed.
                        </p>
                      )}
                    </div>
                  </div>

                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}