import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  Sprout, 
  Droplets, 
  LineChart, 
  ArrowRight, 
  CheckCircle2, 
  Leaf 
} from 'lucide-react';

export default function Landing() {
  const features = [
    {
      icon: <BarChart3 className="w-8 h-8 text-emerald-600" />,
      title: 'Accurate Yield Prediction',
      description: 'Machine learning models trained on historical farm data to predict crop yields with high accuracy.'
    },
    {
      icon: <Leaf className="w-8 h-8 text-emerald-600" />,
      title: 'Crop Recommendation',
      description: 'Get personalized crop recommendations based on your soil conditions and climate patterns.'
    },
    {
      icon: <Droplets className="w-8 h-8 text-emerald-600" />,
      title: 'Soil & Weather Optimization',
      description: 'Optimize your inputs for nitrogen, phosphorus, potassium, water, and temperature management.'
    },
    {
      icon: <LineChart className="w-8 h-8 text-emerald-600" />,
      title: 'Analytics Dashboard',
      description: 'Track your farm performance over time with detailed analytics and historical comparisons.'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.2 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-32 lg:pt-32 lg:pb-48">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-emerald-100/50 blur-[120px] rounded-full" />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-700 text-sm font-medium mb-6">
              <Sprout className="w-4 h-4" /> Next-Gen Farming Intelligence
            </span>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 tracking-tight mb-8">
              Maximize Your <br />
              <span className="text-emerald-600">Harvest Potential</span>
            </h1>
            <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              Predict crop yields with precision using our advanced AI-driven models. 
              Get actionable insights to optimize your farm parameters and maximize output.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/input"
                className="group inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-8 py-4 rounded-2xl text-lg shadow-xl shadow-emerald-200 transition-all hover:scale-105 active:scale-95"
              >
                Start Prediction
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 bg-white hover:bg-gray-50 text-gray-700 font-bold px-8 py-4 rounded-2xl text-lg border border-gray-200 transition-all"
              >
                View Dashboard
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Precision Agriculture</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">Everything you need to transform your farm into a data-driven powerhouse.</p>
          </div>

          <motion.div 
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ y: -8 }}
                className="relative p-8 rounded-3xl border border-gray-100 bg-white hover:shadow-2xl hover:shadow-emerald-500/10 transition-all group"
              >
                <div className="w-16 h-16 rounded-2xl bg-emerald-50 flex items-center justify-center mb-6 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                  {/* We use React.cloneElement to change color on hover if needed, or just let classes handle it */}
                  <div className="group-hover:text-white">
                    {feature.icon}
                  </div>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed text-sm">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative overflow-hidden bg-emerald-900 rounded-[3rem] p-12 sm:p-20 text-center text-white"
          >
            <div className="absolute top-0 right-0 p-8 opacity-10">
              <Sprout className="w-64 h-64 rotate-12" />
            </div>
            
            <h2 className="text-4xl sm:text-5xl font-bold mb-6 relative z-10">
              Ready to Optimize Your Farm?
            </h2>
            <p className="text-xl mb-10 text-emerald-100 max-w-2xl mx-auto relative z-10">
              Join thousands of farmers using data to feed the world more efficiently and sustainably.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 relative z-10">
              {['Smart Recommendations', 'Real-time Analytics', 'Soil Health Tracking'].map((item) => (
                <div key={item} className="flex items-center gap-2 text-emerald-200">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm font-medium">{item}</span>
                </div>
              ))}
            </div>

            <Link
              to="/input"
              className="mt-12 inline-block bg-white hover:bg-emerald-50 text-emerald-900 font-bold px-10 py-5 rounded-2xl text-lg transition-transform hover:scale-105 active:scale-95"
            >
              Get Started Now
            </Link>
          </motion.div>
        </div>
      </section>

      <footer className="py-12 border-t border-gray-100 bg-white text-center text-gray-500 text-sm">
        <p>&copy; 2026 FarmYield Prediction System. All rights reserved.</p>
      </footer>
    </div>
  );
}
