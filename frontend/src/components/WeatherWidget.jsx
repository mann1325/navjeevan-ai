import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { CloudSun, Thermometer, Droplets, CloudRain, ShieldCheck, AlertTriangle, MapPin, RefreshCw } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

const GUJARAT_CITIES = [
  "Surat", "Navsari", "Bardoli", "Anand", "Rajkot", "Ahmedabad", "Vadodara", "Junagadh", "Bhavnagar", "Jamnagar"
];

export default function WeatherWidget() {
  const [selectedCity, setSelectedCity] = useState("Surat");
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWeather = (city) => {
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}/api/v1/weather?location=${city}`)
      .then((res) => {
        if (!res.ok) throw new Error("Weather service unavailable");
        return res.json();
      })
      .then((resData) => {
        if (resData && resData.data) {
          setWeatherData(resData.data);
        } else {
          throw new Error("Invalid weather data format");
        }
      })
      .catch((err) => {
        setWeatherData(null);
        setError(err.message || "Live weather is unavailable");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchWeather(selectedCity);
  }, [selectedCity]);

  const getSprayAdvice = (rainMm) => {
    if (rainMm > 50) {
      return {
        status: "High Rain Risk — Postpone Spraying",
        color: "bg-red-50 text-red-700 border-red-200",
        icon: AlertTriangle,
        desc: "Heavy rain forecasted in next 3 days. Postpone pesticide and fertilizer application to prevent chemical runoff.",
      };
    } else if (rainMm > 15) {
      return {
        status: "Moderate Rain Expected — Exercise Caution",
        color: "bg-amber-50 text-amber-700 border-amber-200",
        icon: AlertTriangle,
        desc: "Light to moderate showers expected. Complete spraying early in the morning before rain clouds build up.",
      };
    } else {
      return {
        status: "Optimal Spraying & Field Conditions",
        color: "bg-emerald-50 text-emerald-700 border-emerald-200",
        icon: ShieldCheck,
        desc: "Dry weather conditions detected. Ideal window for fertilizer top-dressing and crop pest treatment.",
      };
    }
  };

  const advice = weatherData ? getSprayAdvice(weatherData.forecast_3d_rain_mm || 0) : null;
  const AdviceIcon = advice ? advice.icon : ShieldCheck;

  return (
    <section id="weather" className="py-20 bg-white relative">

      <div className="max-w-container mx-auto px-6">
        <div className="bg-gradient-to-br from-primary-dark via-primary to-primary-dark rounded-4xl p-8 sm:p-12 text-white shadow-2xl relative overflow-hidden">
          {/* FLOATING DECORATION */}
          <div className="absolute top-0 right-0 w-80 h-80 bg-accentYellow/10 rounded-full blur-3xl" />

          <div className="relative z-10 grid lg:grid-cols-12 gap-10 items-center">
            {/* LEFT SIDE: SELECTOR & DETAILS */}
            <div className="lg:col-span-5 space-y-6">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-accentYellow text-xs font-semibold uppercase tracking-wider">
                <CloudSun className="w-4 h-4" />
                <span>Live Agricultural Weather Detection</span>
              </div>

              <h2 className="text-3xl sm:text-4xl font-bold font-sans">
                Real-Time <span className="text-accentYellow font-serif italic">Weather & Spray Advisor</span>
              </h2>

              <p className="text-white/80 text-sm leading-relaxed">
                Select your district to detect live temperature, humidity, 3-day rainfall forecast, and AI-recommended pesticide spraying windows.
              </p>

              {/* CITY SELECTOR DROPDOWN */}
              <div className="space-y-2">
                <label className="block text-xs font-bold text-accentYellow uppercase tracking-wider">
                  Select Gujarat District / City
                </label>
                <div className="relative">
                  <select
                    value={selectedCity}
                    onChange={(e) => setSelectedCity(e.target.value)}
                    className="w-full bg-white/10 backdrop-blur-md border border-white/30 rounded-2xl px-5 py-3.5 text-white font-medium text-base outline-none focus:border-accentYellow appearance-none cursor-pointer"
                  >
                    {GUJARAT_CITIES.map((c) => (
                      <option key={c} value={c} className="bg-primary-dark text-white">
                        📍 {c} District
                      </option>
                    ))}
                  </select>
                  <MapPin className="w-5 h-5 text-accentYellow absolute right-4 top-4 pointer-events-none" />
                </div>
              </div>
            </div>

            {/* RIGHT SIDE: LIVE WEATHER METRIC CARDS */}
            <div className="lg:col-span-7">
              {loading ? (
                <div className="p-12 text-center bg-white/10 backdrop-blur-md rounded-3xl border border-white/20">
                  <RefreshCw className="w-8 h-8 text-accentYellow animate-spin mx-auto mb-3" />
                  <p className="text-sm font-medium">Detecting live weather for {selectedCity}...</p>
                </div>
              ) : error ? (
                <div className="p-12 text-center bg-white/10 backdrop-blur-md rounded-3xl border border-red-200/30">
                  <AlertTriangle className="w-8 h-8 text-accentYellow mx-auto mb-3" />
                  <p className="text-sm font-medium">Live weather unavailable for {selectedCity}.</p>
                  <p className="text-xs text-white/70 mt-2">{error}. Please try again later.</p>
                </div>
              ) : weatherData ? (
                <div className="space-y-6">
                  <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-white/75">
                    <span>
                      Data status: {weatherData.status === "fallback" ? "Fallback provider" : weatherData.status || "Unavailable"}
                    </span>
                    <span>
                      Source: {weatherData.source || "Unknown"}
                      {weatherData.fetched_at ? ` · ${new Date(weatherData.fetched_at).toLocaleString()}` : ""}
                    </span>
                  </div>
                  {/* METRICS GRID */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white/10 backdrop-blur-md p-5 rounded-3xl border border-white/20 text-center">
                      <Thermometer className="w-6 h-6 text-accentYellow mx-auto mb-2" />
                      <div className="text-xs text-white/70 uppercase tracking-wider font-medium">Temperature</div>
                      <div className="text-2xl sm:text-3xl font-bold font-sans text-white mt-1">
                        {weatherData.temp_c}°C
                      </div>
                    </div>

                    <div className="bg-white/10 backdrop-blur-md p-5 rounded-3xl border border-white/20 text-center">
                      <Droplets className="w-6 h-6 text-lightGreen mx-auto mb-2" />
                      <div className="text-xs text-white/70 uppercase tracking-wider font-medium">Humidity</div>
                      <div className="text-2xl sm:text-3xl font-bold font-sans text-white mt-1">
                        {weatherData.humidity_percent}%
                      </div>
                    </div>

                    <div className="bg-white/10 backdrop-blur-md p-5 rounded-3xl border border-white/20 text-center">
                      <CloudRain className="w-6 h-6 text-sky-400 mx-auto mb-2" />
                      <div className="text-xs text-white/70 uppercase tracking-wider font-medium">3-Day Rain</div>
                      <div className="text-2xl sm:text-3xl font-bold font-sans text-white mt-1">
                        {weatherData.forecast_3d_rain_mm} mm
                      </div>
                    </div>
                  </div>

                  {/* SPRAY RISK ADVISORY BOX */}
                  {advice && (
                    <div className={`p-6 rounded-3xl border ${advice.color} backdrop-blur-md`}>
                      <div className="flex items-center gap-3 mb-2">
                        <AdviceIcon className="w-6 h-6 flex-shrink-0" />
                        <h4 className="font-bold text-base">{advice.status}</h4>
                      </div>
                      <p className="text-xs leading-relaxed opacity-90">{advice.desc}</p>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
