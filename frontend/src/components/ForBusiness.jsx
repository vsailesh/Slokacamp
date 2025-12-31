import React, { useState } from 'react';
import Navbar from './Navbar';
import Footer from './Footer';

const ForBusiness = () => {
  const [formData, setFormData] = useState({
    companyName: '',
    contactName: '',
    email: '',
    phone: '',
    employees: '',
    message: '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Thank you for your interest! Our team will contact you within 24 hours.');
    setFormData({
      companyName: '',
      contactName: '',
      email: '',
      phone: '',
      employees: '',
      message: '',
    });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">SlokaCamp for Business</h1>
          <p className="text-xl text-purple-100 max-w-3xl">
            Empower your team with wellness training, stress management, and mindfulness programs
            from ancient Indian wisdom traditions.
          </p>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Why Choose SlokaCamp for Your Organization?</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Invest in your team's wellbeing and productivity with our corporate wellness programs.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-8 rounded-lg shadow-md">
            <div className="text-4xl mb-4">📈</div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Boost Productivity</h3>
            <p className="text-gray-600">
              Reduce stress and burnout with mindfulness and meditation training, leading to 25% increase in productivity.
            </p>
          </div>
          
          <div className="bg-white p-8 rounded-lg shadow-md">
            <div className="text-4xl mb-4">💪</div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Improve Health</h3>
            <p className="text-gray-600">
              Ayurvedic wellness programs and yoga sessions help employees maintain physical and mental health.
            </p>
          </div>
          
          <div className="bg-white p-8 rounded-lg shadow-md">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Retain Talent</h3>
            <p className="text-gray-600">
              Show you care about employee wellbeing. Companies with wellness programs see 50% lower turnover.
            </p>
          </div>
        </div>

        {/* Features */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">What We Offer</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-semibold text-lg text-gray-900 mb-3">🧘 Corporate Wellness Programs</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Weekly yoga and meditation sessions</li>
                <li>• Stress management workshops</li>
                <li>• Ayurvedic health consultations</li>
                <li>• Breathwork and pranayama training</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-lg text-gray-900 mb-3">📚 Learning & Development</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Access to 500+ courses on wellness</li>
                <li>• Custom learning paths for teams</li>
                <li>• Live workshops and masterclasses</li>
                <li>• Certification programs</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-lg text-gray-900 mb-3">📊 Analytics & Insights</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Track employee engagement</li>
                <li>• Monitor wellness progress</li>
                <li>• ROI reports and metrics</li>
                <li>• Custom dashboards</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-lg text-gray-900 mb-3">🎓 Expert Support</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Dedicated account manager</li>
                <li>• On-site or virtual sessions</li>
                <li>• Customized curriculum</li>
                <li>• 24/7 technical support</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Pricing Tiers */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Flexible Plans for Every Team Size</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg shadow-md p-8 border-2 border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Starter</h3>
              <div className="text-3xl font-bold text-purple-600 mb-4">₹999<span className="text-lg text-gray-600">/user/month</span></div>
              <ul className="space-y-3 mb-6">
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Up to 50 employees</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Full course library access</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Monthly live sessions</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Basic analytics</span>
                </li>
              </ul>
              <button className="w-full bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 transition-colors font-semibold">
                Contact Sales
              </button>
            </div>
            
            <div className="bg-white rounded-lg shadow-xl p-8 border-2 border-purple-600 relative">
              <div className="absolute top-0 right-0 bg-purple-600 text-white px-4 py-1 text-sm rounded-bl-lg">
                Popular
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Growth</h3>
              <div className="text-3xl font-bold text-purple-600 mb-4">₹799<span className="text-lg text-gray-600">/user/month</span></div>
              <ul className="space-y-3 mb-6">
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">51-200 employees</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Everything in Starter</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Weekly live sessions</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Advanced analytics</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Custom learning paths</span>
                </li>
              </ul>
              <button className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition-colors font-semibold">
                Contact Sales
              </button>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-8 border-2 border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Enterprise</h3>
              <div className="text-3xl font-bold text-purple-600 mb-4">Custom</div>
              <ul className="space-y-3 mb-6">
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">200+ employees</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Everything in Growth</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Dedicated account manager</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">On-site workshops</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600">✓</span>
                  <span className="text-gray-600">Custom integrations</span>
                </li>
              </ul>
              <button className="w-full bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 transition-colors font-semibold">
                Contact Sales
              </button>
            </div>
          </div>
        </div>

        {/* Contact Form */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Get Started Today</h2>
          <p className="text-gray-600 mb-6">
            Fill out the form below and our team will reach out to discuss your organization's needs.
          </p>
          
          <form onSubmit={handleSubmit} className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name *
              </label>
              <input
                type="text"
                name="companyName"
                value={formData.companyName}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contact Name *
              </label>
              <input
                type="text"
                name="contactName"
                value={formData.contactName}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Work Email *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number *
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Employees *
              </label>
              <select
                name="employees"
                value={formData.employees}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">Select...</option>
                <option value="1-50">1-50</option>
                <option value="51-200">51-200</option>
                <option value="201-500">201-500</option>
                <option value="501-1000">501-1000</option>
                <option value="1000+">1000+</option>
              </select>
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tell us about your needs
              </label>
              <textarea
                name="message"
                value={formData.message}
                onChange={handleChange}
                rows="4"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="What are your wellness goals for your team?"
              />
            </div>
            
            <div className="md:col-span-2">
              <button
                type="submit"
                className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition-colors font-semibold"
              >
                Request Demo
              </button>
            </div>
          </form>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default ForBusiness;
