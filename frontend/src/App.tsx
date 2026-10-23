import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, Zap, AlertCircle, Clock } from 'lucide-react';
import { format, parseISO } from 'date-fns';

interface DataPoint {
  start_time_utc: string;
  publish_time_utc: string | null;
  forecast_mw: number | null;
  actual_mw: number | null;
  error: number | null;
}

interface Metadata {
  delivery_date: string;
  cutoff_applied_utc: string;
  total_forecast_mwh: number;
  mae_mw: number;
  missing_actuals: number;
}

export default function App() {
  const [deliveryDate, setDeliveryDate] = useState('2026-01-05');
  const [cutoff, setCutoff] = useState('09:00');
  const [data, setData] = useState<DataPoint[]>([]);
  const [metadata, setMetadata] = useState<Metadata | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/decision?delivery_date=${deliveryDate}&cutoff=${cutoff}`);
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || 'Failed to fetch data');
        }
        const json = await response.json();
        setData(json.data);
        setMetadata(json.metadata);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [deliveryDate, cutoff]);

  const formatTime = (isoString: string) => {
    if (!isoString) return '';
    return format(parseISO(isoString), 'HH:mm');
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-300 p-4 md:p-6 font-sans selection:bg-cyan-500/30">
      <div className="max-w-7xl mx-auto space-y-4">
        
        {/* Header & Controls - Flat & Utilitarian */}
        <div className="bg-[#18181b] border-b border-zinc-800 p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="flex items-center gap-4">
            <div className="w-1.5 h-8 bg-cyan-500 rounded-sm"></div>
            <div>
              <h1 className="text-xl font-semibold text-zinc-100 tracking-tight">Wind Asset Arbitration</h1>
              <p className="text-xs text-zinc-500 font-mono mt-0.5">UK DAY-AHEAD MARKET :: GATE CLOSURE ANALYSIS</p>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center bg-[#09090b] border border-zinc-800 rounded px-3 py-1.5">
              <label className="text-xs font-semibold text-zinc-500 mr-3 uppercase">Delivery Date</label>
              <input 
                type="date" 
                value={deliveryDate}
                min="2026-01-02"
                max="2026-02-01"
                onChange={(e) => setDeliveryDate(e.target.value)}
                className="bg-transparent text-zinc-200 font-mono text-sm focus:outline-none cursor-pointer"
              />
            </div>
            <div className="flex items-center bg-[#09090b] border border-zinc-800 rounded px-3 py-1.5">
              <label className="text-xs font-semibold text-zinc-500 mr-3 uppercase">Gate (D-1)</label>
              <input 
                type="time" 
                value={cutoff}
                onChange={(e) => setCutoff(e.target.value)}
                className="bg-transparent text-amber-500 font-mono text-sm focus:outline-none cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-950/30 border border-red-900 p-4 text-red-400 flex items-center gap-3">
            <AlertCircle size={18} />
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {/* KPI Cards - Dense & Financial */}
        {!error && metadata && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-[#18181b] p-4 border border-zinc-800 flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-[11px] text-zinc-500 font-bold uppercase tracking-widest">Total Forecast</span>
                <Zap size={16} className="text-zinc-600" />
              </div>
              <div>
                <span className="text-3xl font-mono font-medium text-zinc-100">{metadata.total_forecast_mwh.toLocaleString()}</span>
                <span className="text-xs text-zinc-500 ml-2">MWh</span>
              </div>
            </div>
            
            <div className="bg-[#18181b] p-4 border border-zinc-800 flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-[11px] text-zinc-500 font-bold uppercase tracking-widest">Risk Exposure (MAE)</span>
                <Activity size={16} className="text-amber-500" />
              </div>
              <div>
                <span className="text-3xl font-mono font-medium text-amber-500">{metadata.mae_mw.toLocaleString(undefined, {maximumFractionDigits: 0})}</span>
                <span className="text-xs text-amber-700 ml-2">MW</span>
              </div>
            </div>

            <div className="bg-[#18181b] p-4 border border-zinc-800 flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-[11px] text-zinc-500 font-bold uppercase tracking-widest">Forecast Vintage</span>
                <Clock size={16} className="text-zinc-600" />
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-mono font-medium text-zinc-300">{format(parseISO(metadata.cutoff_applied_utc), 'dd MMM yyyy')}</span>
                <span className="text-sm font-mono text-zinc-500">{format(parseISO(metadata.cutoff_applied_utc), 'HH:mm')} UTC</span>
              </div>
            </div>

            <div className="bg-[#18181b] p-4 border border-zinc-800 flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-[11px] text-zinc-500 font-bold uppercase tracking-widest">Data Integrity</span>
                <AlertCircle size={16} className={metadata.missing_actuals > 0 ? "text-red-500" : "text-zinc-600"} />
              </div>
              <div>
                <span className={`text-3xl font-mono font-medium ${metadata.missing_actuals > 0 ? "text-red-500" : "text-zinc-400"}`}>{metadata.missing_actuals}</span>
                <span className="text-xs text-zinc-600 ml-2">missing slots</span>
              </div>
            </div>
          </div>
        )}

        {/* Chart Area - Advanced Area Chart */}
        {!error && (
          <div className="bg-[#18181b] p-5 border border-zinc-800">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Intraday Profile: Actual vs Forecast</h2>
            </div>
            
            <div className="h-[500px] w-full">
              {loading ? (
                <div className="w-full h-full flex items-center justify-center font-mono text-sm text-zinc-500">
                  FETCHING GRID DATA...
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                    <defs>
                      <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#fbbf24" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#27272a" />
                    <XAxis 
                      dataKey="start_time_utc" 
                      tickFormatter={formatTime} 
                      minTickGap={45}
                      stroke="#52525b"
                      tick={{ fill: '#71717a', fontSize: 11, fontFamily: 'monospace' }}
                      axisLine={{ stroke: '#27272a' }}
                    />
                    <YAxis 
                      stroke="#52525b" 
                      tick={{ fill: '#71717a', fontSize: 11, fontFamily: 'monospace' }}
                      tickFormatter={(val) => `${val.toLocaleString()}`}
                      axisLine={false}
                      tickLine={false}
                      width={65}
                    />
                    <Tooltip 
                      labelFormatter={(label) => `TIME: ${formatTime(label as string)}`}
                      formatter={(value: number, name: string) => [`${value.toLocaleString()} MW`, name]}
                      contentStyle={{ 
                        backgroundColor: '#09090b', 
                        borderColor: '#27272a', 
                        color: '#f4f4f5',
                        fontFamily: 'monospace',
                        fontSize: '12px',
                        borderRadius: '4px'
                      }}
                      itemStyle={{ paddingTop: '4px' }}
                    />
                    <Legend 
                      iconType="circle" 
                      wrapperStyle={{ fontSize: '12px', color: '#a1a1aa' }}
                    />
                    <Area 
                      type="stepAfter" 
                      dataKey="actual_mw" 
                      name="Actual Generation" 
                      stroke="#06b6d4" 
                      fillOpacity={1} 
                      fill="url(#colorActual)" 
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4, fill: '#06b6d4', stroke: '#09090b', strokeWidth: 2 }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="forecast_mw" 
                      name="Gate Closure Forecast" 
                      stroke="#fbbf24" 
                      fillOpacity={1} 
                      fill="url(#colorForecast)" 
                      strokeWidth={2}
                      strokeDasharray="4 4"
                      dot={false}
                      connectNulls={true}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}