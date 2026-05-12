import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FarmForm from '../components/FarmForm';
import ResultCard from '../components/ResultCard';
import { HelpCircle, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { useAuth } from '../context/AuthContext';

const API_BASE = '/api/v1';

export default function Input() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [apiError, setApiError] = useState(null);

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    setFieldErrors({});
    setApiError(null);

    try {
      const payload = {
        ...formData,
        nitrogen: parseFloat(formData.nitrogen),
        phosphorus: parseFloat(formData.phosphorus),
        potassium: parseFloat(formData.potassium),
        ph: parseFloat(formData.ph),
        temperature: parseFloat(formData.temperature),
        rainfall: parseFloat(formData.rainfall),
        farm_size_ha: parseFloat(formData.farm_size_ha || 1.0)
      };

      const response = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (!response.ok || result.status === 'error') {
        // If we have field-specific errors from the backend
        if (result.errors) {
          setFieldErrors(result.errors);
          throw new Error("Please correct the highlighted fields.");
        }
        throw new Error(result.message || `Server error: ${response.status}`);
      }

      // Navigate to result page and pass both the raw form inputs and the API prediction
      navigate('/result', {
        state: {
          formData,
          prediction: result.data,
        },
      });
    } catch (err) {
      console.error('Prediction error:', err);
      setApiError(err.message || 'Failed to connect to the prediction server. Is the backend running?');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/50 py-16">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <header className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 tracking-tight mb-2">
            Farm Prediction
          </h1>
          <p className="text-gray-500 font-medium">
            Enter your farm parameters to get a yield prediction and optimization recommendations.
          </p>
        </header>

        <AnimatePresence>
          {apiError && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8 p-5 rounded-2xl bg-red-50 border border-red-100 text-red-700 text-sm flex items-center gap-3"
            >
              <AlertTriangle className="w-5 h-5 shrink-0" />
              <span>{apiError}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <ResultCard title="Environmental Parameters">
          <FarmForm onSubmit={handleSubmit} isLoading={isLoading} errors={fieldErrors} />
        </ResultCard>

        <div className="mt-12 bg-white rounded-[2rem] border border-emerald-100 p-8 shadow-sm shadow-emerald-500/5">
          <div className="flex items-center gap-2 mb-4">
            <HelpCircle className="w-5 h-5 text-emerald-600" />
            <h3 className="font-bold text-gray-900 text-lg tracking-tight">Parameter Guide</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-sm">
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                <p className="text-gray-600"><span className="font-bold text-gray-900">Soil Nutrients (N, P, K):</span> Measured in kg per hectare. These represent the primary macronutrients available in your soil.</p>
              </div>
              <div className="flex gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                <p className="text-gray-600"><span className="font-bold text-gray-900">Soil pH:</span> On a scale of 0-14. Most crops thrive between 6.0 and 7.5 (slightly acidic to neutral).</p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                <p className="text-gray-600"><span className="font-bold text-gray-900">Climate Factors:</span> Temperature is key for predicting irrigation needs and disease risk.</p>
              </div>
              <div className="flex gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                <p className="text-gray-600"><span className="font-bold text-gray-900">Rainfall:</span> Annual average in mm. Essential for calculating natural water availability versus artificial irrigation.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}