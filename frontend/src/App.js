import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Import UI components
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Alert, AlertDescription } from './components/ui/alert';
import { Progress } from './components/ui/progress';
import { toast } from './hooks/use-toast';
import { Toaster } from './components/ui/toaster';

// Icons
import { AlertTriangle, Brain, Globe, Shield, TrendingUp, Users, Plus, Play, Eye, MessageSquare, BookOpen, CheckSquare, Target, FileText, Download, Activity, Zap, BarChart3, Network, Layers, Cpu, Monitor, TrendingDown, Link, Cloud, Lightbulb, Rss, Database, Timer, Share2, ExternalLink, Building2, Upload, Users2, Settings, BarChart, TrendingUp as TrendingUpIcon, Briefcase } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserProfile();
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(`${API}/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      logout();
    }
  };

  const login = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => React.useContext(AuthContext);

// Auth Components
const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    organization: '',
    job_title: '',
    department: ''
  });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = isLogin ? '/login' : '/register';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : formData;

      const response = await axios.post(`${API}${endpoint}`, payload);
      login(response.data.access_token);
      toast({ title: "Success", description: `${isLogin ? 'Logged in' : 'Registered'} successfully!` });
    } catch (error) {
      toast({ 
        title: "Error", 
        description: error.response?.data?.detail || `${isLogin ? 'Login' : 'Registration'} failed`,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4 relative">
      <div className="absolute inset-0 opacity-20" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='m36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
      }}></div>
      
      <Card className="w-full max-w-md backdrop-blur-xl bg-white/10 border-white/20 shadow-2xl">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-white flex items-center justify-center gap-2">
            <Brain className="w-8 h-8 text-blue-400" />
            Polycrisis Simulator
          </CardTitle>
          <CardDescription className="text-gray-300">
            Simulate, Analyze, and Mitigate Complex Crises with AI
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={isLogin ? "login" : "register"} onValueChange={(value) => setIsLogin(value === "login")}>
            <TabsList className="grid w-full grid-cols-2 bg-white/10">
              <TabsTrigger value="login" className="text-white data-[state=active]:bg-blue-500">Login</TabsTrigger>
              <TabsTrigger value="register" className="text-white data-[state=active]:bg-blue-500">Register</TabsTrigger>
            </TabsList>
            
            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <TabsContent value="login" className="space-y-4">
                <div>
                  <Label htmlFor="email" className="text-white">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    placeholder="Enter your email"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="password" className="text-white">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    placeholder="Enter your password"
                    required
                  />
                </div>
              </TabsContent>
              
              <TabsContent value="register" className="space-y-4">
                <div>
                  <Label htmlFor="email" className="text-white">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    placeholder="Enter your email"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="username" className="text-white">Username</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    placeholder="Choose a username"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="organization" className="text-white">Organization</Label>
                  <Input
                    id="organization"
                    value={formData.organization}
                    onChange={(e) => setFormData({...formData, organization: e.target.value})}
                    className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    placeholder="Your organization name"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="job_title" className="text-white">Job Title</Label>
                  <Input
                    id="job_title"
                    value={formData.job_title || ''}
                    onChange={(e) => setFormData({...formData, job_title: e.target.value})}
                    className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    placeholder="Your job title (optional)"
                  />
                </div>
                <div>
                  <Label htmlFor="department" className="text-white">Department</Label>
                  <Input
                    id="department"
                    value={formData.department || ''}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    placeholder="Your department (optional)"
                  />
                </div>
                <div>
                  <Label htmlFor="password" className="text-white">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    placeholder="Create a password"
                    required
                  />
                </div>
              </TabsContent>
              
              <Button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700 text-white" 
                disabled={loading}
              >
                {loading ? 'Processing...' : (isLogin ? 'Login' : 'Register')}
              </Button>
            </form>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

// Advanced Analytics Dashboard
const AdvancedDashboard = () => {
  const [stats, setStats] = useState({});
  const [scenarios, setScenarios] = useState([]);
  const [advancedAnalytics, setAdvancedAnalytics] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdvancedDashboardData();
  }, []);

  const fetchAdvancedDashboardData = async () => {
    try {
      const [statsRes, scenariosRes, analyticsRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/scenarios`),
        axios.get(`${API}/dashboard/advanced-analytics`)
      ]);
      setStats(statsRes.data);
      setScenarios(scenariosRes.data);
      setAdvancedAnalytics(analyticsRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    if (score >= 0.4) return 'text-orange-600';
    return 'text-red-600';
  };

  const getHealthScoreBg = (score) => {
    if (score >= 0.8) return 'bg-green-50 border-green-200';
    if (score >= 0.6) return 'bg-yellow-50 border-yellow-200';
    if (score >= 0.4) return 'bg-orange-50 border-orange-200';
    return 'bg-red-50 border-red-200';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Brain className="w-12 h-12 animate-pulse text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading advanced analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* System Health Overview */}
      <Card className={`${getHealthScoreBg(advancedAnalytics.system_health_score || 0.5)}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">System Health Score</h3>
              <p className="text-sm text-gray-600">Overall polycrisis simulation system performance</p>
            </div>
            <div className="text-right">
              <div className={`text-4xl font-bold ${getHealthScoreColor(advancedAnalytics.system_health_score || 0.5)}`}>
                {Math.round((advancedAnalytics.system_health_score || 0.5) * 100)}%
              </div>
              <div className="flex items-center gap-1 text-sm text-gray-600">
                <Activity className="w-4 h-4" />
                <span>{advancedAnalytics.monitoring_coverage || 'Basic'} Monitoring</span>
              </div>
            </div>
          </div>
          
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {Math.round((advancedAnalytics.average_resilience_score || 0.5) * 100)}%
              </div>
              <div className="text-xs text-gray-600">Resilience Score</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {advancedAnalytics.total_monitor_agents || 0}
              </div>
              <div className="text-xs text-gray-600">AI Monitors</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {advancedAnalytics.learning_insights_generated || 0}
              </div>
              <div className="text-xs text-gray-600">Learning Insights</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {advancedAnalytics.complex_systems_analyzed || 0}
              </div>
              <div className="text-xs text-gray-600">Complex Systems</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Advanced Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 font-medium">Active Scenarios</p>
                <p className="text-3xl font-bold text-blue-900">{stats.active_scenarios || 0}</p>
                <p className="text-xs text-blue-700">of {stats.total_scenarios || 0} total</p>
              </div>
              <Globe className="w-10 h-10 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600 font-medium">AI Monitor Agents</p>
                <p className="text-3xl font-bold text-purple-900">{advancedAnalytics.total_monitor_agents || 0}</p>
                <p className="text-xs text-purple-700">Real-time monitoring</p>
              </div>
              <Monitor className="w-10 h-10 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600 font-medium">Adaptive Learning</p>
                <p className="text-3xl font-bold text-green-900">
                  {advancedAnalytics.adaptive_learning_active ? 'ON' : 'OFF'}
                </p>
                <p className="text-xs text-green-700">{advancedAnalytics.learning_insights_generated || 0} insights</p>
              </div>
              <Brain className="w-10 h-10 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-orange-600 font-medium">Complex Systems</p>
                <p className="text-3xl font-bold text-orange-900">{advancedAnalytics.complex_systems_analyzed || 0}</p>
                <p className="text-xs text-orange-700">Analyzed systems</p>
              </div>
              <Network className="w-10 h-10 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Real-Time Analytics Section */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              System Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Resilience Score</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{width: `${(advancedAnalytics.average_resilience_score || 0.5) * 100}%`}}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{Math.round((advancedAnalytics.average_resilience_score || 0.5) * 100)}%</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">System Health</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{width: `${(advancedAnalytics.system_health_score || 0.5) * 100}%`}}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{Math.round((advancedAnalytics.system_health_score || 0.5) * 100)}%</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Monitoring Coverage</span>
                <Badge variant="outline" className="text-xs">
                  {advancedAnalytics.monitoring_coverage || 'Basic'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-purple-600" />
              AI Monitor Agents Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium text-green-800">Risk Monitor</span>
                </div>
                <Badge className="bg-green-100 text-green-800">Active</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm font-medium text-blue-800">Performance Tracker</span>
                </div>
                <Badge className="bg-blue-100 text-blue-800">Active</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-200">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <span className="text-sm font-medium text-orange-800">Anomaly Detector</span>
                </div>
                <Badge className="bg-orange-100 text-orange-800">Monitoring</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-sm font-medium text-purple-800">Trend Analyzer</span>
                </div>
                <Badge className="bg-purple-100 text-purple-800">Learning</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Scenarios with Enhanced Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Enhanced Scenarios with AI Monitoring
          </CardTitle>
        </CardHeader>
        <CardContent>
          {scenarios.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Globe className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No scenarios created yet. Start by creating your first crisis scenario with AI monitoring.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {scenarios.slice(0, 3).map((scenario) => (
                <div key={scenario.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{scenario.title}</h3>
                    <p className="text-sm text-gray-600 truncate">{scenario.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={scenario.status === 'active' ? 'default' : 'secondary'}>
                        {scenario.status}
                      </Badge>
                      <Badge variant="outline">{scenario.crisis_type}</Badge>
                      <span className="text-xs text-gray-500">Severity: {scenario.severity_level}/10</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Monitor className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Network className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Basic Dashboard (keeping for compatibility)
const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, scenariosRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/scenarios`)
      ]);
      setStats(statsRes.data);
      setScenarios(scenariosRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Brain className="w-12 h-12 animate-pulse text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 font-medium">Total Scenarios</p>
                <p className="text-3xl font-bold text-blue-900">{stats.total_scenarios || 0}</p>
              </div>
              <Globe className="w-10 h-10 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600 font-medium">Active Scenarios</p>
                <p className="text-3xl font-bold text-green-900">{stats.active_scenarios || 0}</p>
              </div>
              <TrendingUp className="w-10 h-10 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600 font-medium">Simulations Run</p>
                <p className="text-3xl font-bold text-purple-900">{stats.total_simulations || 0}</p>
              </div>
              <Brain className="w-10 h-10 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-orange-600 font-medium">Organization</p>
                <p className="text-lg font-bold text-orange-900 truncate">{stats.user_organization || 'N/A'}</p>
              </div>
              <Users className="w-10 h-10 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Scenarios */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Recent Scenarios
          </CardTitle>
        </CardHeader>
        <CardContent>
          {scenarios.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Globe className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No scenarios created yet. Start by creating your first crisis scenario.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {scenarios.slice(0, 5).map((scenario) => (
                <div key={scenario.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{scenario.title}</h3>
                    <p className="text-sm text-gray-600 truncate">{scenario.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={scenario.status === 'active' ? 'default' : 'secondary'}>
                        {scenario.status}
                      </Badge>
                      <Badge variant="outline">{scenario.crisis_type}</Badge>
                      <span className="text-xs text-gray-500">Severity: {scenario.severity_level}/10</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Play className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Scenario Creation Component
const ScenarioCreator = ({ onScenarioCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    crisis_type: '',
    severity_level: 5,
    affected_regions: [],
    key_variables: []
  });
  const [regionInput, setRegionInput] = useState('');
  const [variableInput, setVariableInput] = useState('');
  const [loading, setLoading] = useState(false);

  const crisisTypes = [
    'natural_disaster',
    'economic_crisis', 
    'social_unrest',
    'pandemic',
    'cyber_attack',
    'supply_chain_disruption',
    'climate_change',
    'political_instability'
  ];

  const addRegion = () => {
    if (regionInput.trim() && !formData.affected_regions.includes(regionInput.trim())) {
      setFormData({
        ...formData,
        affected_regions: [...formData.affected_regions, regionInput.trim()]
      });
      setRegionInput('');
    }
  };

  const addVariable = () => {
    if (variableInput.trim() && !formData.key_variables.includes(variableInput.trim())) {
      setFormData({
        ...formData,
        key_variables: [...formData.key_variables, variableInput.trim()]
      });
      setVariableInput('');
    }
  };

  const removeRegion = (region) => {
    setFormData({
      ...formData,
      affected_regions: formData.affected_regions.filter(r => r !== region)
    });
  };

  const removeVariable = (variable) => {
    setFormData({
      ...formData,
      key_variables: formData.key_variables.filter(v => v !== variable)
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/scenarios`, formData);
      toast({ title: "Success", description: "Scenario created successfully!" });
      onScenarioCreated(response.data);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        crisis_type: '',
        severity_level: 5,
        affected_regions: [],
        key_variables: []
      });
    } catch (error) {
      toast({ 
        title: "Error", 
        description: error.response?.data?.detail || "Failed to create scenario",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Create New Crisis Scenario
        </CardTitle>
        <CardDescription>
          Define a complex crisis scenario for AI-powered analysis and simulation
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="title">Scenario Title</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              placeholder="e.g., Major Earthquake in Metropolitan Area"
              required
            />
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Detailed description of the crisis scenario..."
              rows={4}
              required
            />
          </div>

          <div>
            <Label htmlFor="crisis_type">Crisis Type</Label>
            <Select value={formData.crisis_type} onValueChange={(value) => setFormData({...formData, crisis_type: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Select crisis type" />
              </SelectTrigger>
              <SelectContent>
                {crisisTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="severity">Severity Level: {formData.severity_level}/10</Label>
            <input
              type="range"
              id="severity"
              min="1"
              max="10"
              value={formData.severity_level}
              onChange={(e) => setFormData({...formData, severity_level: parseInt(e.target.value)})}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>

          <div>
            <Label>Affected Regions</Label>
            <div className="flex gap-2 mb-2">
              <Input
                value={regionInput}
                onChange={(e) => setRegionInput(e.target.value)}
                placeholder="Add region (e.g., California, Tokyo)"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addRegion())}
              />
              <Button type="button" onClick={addRegion} variant="outline" size="sm">
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.affected_regions.map((region) => (
                <Badge key={region} variant="secondary" className="cursor-pointer" onClick={() => removeRegion(region)}>
                  {region} ×
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <Label>Key Variables</Label>
            <div className="flex gap-2 mb-2">
              <Input
                value={variableInput}
                onChange={(e) => setVariableInput(e.target.value)}
                placeholder="Add variable (e.g., Population density, Infrastructure age)"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addVariable())}
              />
              <Button type="button" onClick={addVariable} variant="outline" size="sm">
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.key_variables.map((variable) => (
                <Badge key={variable} variant="secondary" className="cursor-pointer" onClick={() => removeVariable(variable)}>
                  {variable} ×
                </Badge>
              ))}
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Creating...' : 'Create Scenario'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

// AI Genie Component
const AIGenie = ({ selectedScenario }) => {
  const [query, setQuery] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { type: 'user', content: query, timestamp: new Date() };
    setConversation([...conversation, userMessage]);
    setLoading(true);

    try {
      const response = await axios.post(`${API}/ai-genie`, {
        scenario_id: selectedScenario?.id,
        user_query: query,
        context: selectedScenario ? JSON.stringify(selectedScenario) : null
      });

      const aiMessage = {
        type: 'assistant',
        content: response.data.response,
        suggestions: response.data.suggestions,
        monitoring_tasks: response.data.monitoring_tasks,
        timestamp: new Date()
      };

      setConversation(prev => [...prev, aiMessage]);
      setQuery('');
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to get AI response",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5" />
          AI Avatar Genie
        </CardTitle>
        <CardDescription>
          Get intelligent insights and suggestions for your crisis scenarios
          {selectedScenario && (
            <Badge variant="outline" className="ml-2">
              {selectedScenario.title}
            </Badge>
          )}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-gray-50 rounded-lg">
          {conversation.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Start a conversation with the AI Avatar Genie</p>
              <p className="text-sm">Ask for scenario insights, monitoring tasks, or mitigation strategies</p>
            </div>
          ) : (
            conversation.map((message, index) => (
              <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-lg ${
                  message.type === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-white border shadow-sm'
                }`}>
                  <p className="text-sm">{message.content}</p>
                  {message.suggestions && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs font-semibold text-gray-600 mb-2">Suggestions:</p>
                      <ul className="text-xs space-y-1">
                        {message.suggestions.map((suggestion, i) => (
                          <li key={i} className="text-gray-700">• {suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {message.monitoring_tasks && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs font-semibold text-gray-600 mb-2">Monitoring Tasks:</p>
                      <ul className="text-xs space-y-1">
                        {message.monitoring_tasks.map((task, i) => (
                          <li key={i} className="text-gray-700">• {task}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border shadow-sm p-3 rounded-lg">
                <div className="flex items-center gap-2">
                  <Brain className="w-4 h-4 animate-pulse text-blue-500" />
                  <span className="text-sm text-gray-600">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask the AI Genie about your scenario..."
            disabled={loading}
          />
          <Button type="submit" disabled={loading || !query.trim()}>
            Send
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

// Scenario Management Component
const ScenarioManagement = ({ onScenarioSelect }) => {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [scenarioToDelete, setScenarioToDelete] = useState(null);
  const [editingScenario, setEditingScenario] = useState(null);
  const [implementationView, setImplementationView] = useState(null);
  const [implementationData, setImplementationData] = useState({});
  const [generatingImplementation, setGeneratingImplementation] = useState(false);
  const [monitorAgents, setMonitorAgents] = useState({});
  const [deployingMonitors, setDeployingMonitors] = useState(false);
  const [systemMetrics, setSystemMetrics] = useState({});
  const [complexSystems, setComplexSystems] = useState({});
  const [learningInsights, setLearningInsights] = useState({});
  const [monitoringSources, setMonitoringSources] = useState({});
  const [smartSuggestions, setSmartSuggestions] = useState({});
  const [monitoringDashboard, setMonitoringDashboard] = useState({});
  const [showMonitoringDialog, setShowMonitoringDialog] = useState(null);
  const [showAddSourceDialog, setShowAddSourceDialog] = useState(null);
  const [newSourceData, setNewSourceData] = useState({
    source_type: '',
    source_url: '',
    source_name: '',
    monitoring_frequency: 'daily',
    data_keywords: []
  });

  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchScenarios = async () => {
    try {
      const response = await axios.get(`${API}/scenarios`);
      setScenarios(response.data);
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to fetch scenarios",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteScenario = async (scenarioId) => {
    try {
      await axios.delete(`${API}/scenarios/${scenarioId}`);
      setScenarios(scenarios.filter(s => s.id !== scenarioId));
      setShowDeleteDialog(false);
      setScenarioToDelete(null);
      toast({ title: "Success", description: "Scenario deleted successfully" });
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to delete scenario",
        variant: "destructive"
      });
    }
  };

  const handleRunSimulation = async (scenario) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/scenarios/${scenario.id}/simulate`);
      
      // Update scenario status to active
      const updatedScenarios = scenarios.map(s => 
        s.id === scenario.id ? { ...s, status: 'active' } : s
      );
      setScenarios(updatedScenarios);
      
      toast({ 
        title: "Success", 
        description: "Simulation completed successfully!",
        duration: 5000
      });
      
      // Show results in a dialog or navigate to results view
      setSelectedScenario({ ...scenario, simulation_result: response.data });
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to run simulation",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateImplementation = async (scenario, type) => {
    try {
      setGeneratingImplementation(true);
      let endpoint = '';
      
      switch(type) {
        case 'game-book':
          endpoint = `scenarios/${scenario.id}/game-book`;
          break;
        case 'action-plan':
          endpoint = `scenarios/${scenario.id}/action-plan`;
          break;
        case 'strategy-implementation':
          endpoint = `scenarios/${scenario.id}/strategy-implementation`;
          break;
        default:
          return;
      }
      
      const response = await axios.post(`${API}/${endpoint}`);
      setImplementationData({
        ...implementationData,
        [scenario.id]: {
          ...implementationData[scenario.id],
          [type]: response.data
        }
      });
      
      setImplementationView({ scenario, type, data: response.data });
      
      toast({ 
        title: "Success", 
        description: `${type.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())} generated successfully!`,
        duration: 3000
      });
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: `Failed to generate ${type.replace('-', ' ')}`,
        variant: "destructive"
      });
    } finally {
      setGeneratingImplementation(false);
    }
  };

  const handleSuggestMonitoringSources = async (scenario) => {
    try {
      setGeneratingImplementation(true);
      const response = await axios.post(`${API}/scenarios/${scenario.id}/suggest-monitoring-sources`);
      setSmartSuggestions({
        ...smartSuggestions,
        [scenario.id]: response.data
      });
      
      setImplementationView({ scenario, type: 'monitoring-suggestions', data: response.data });
      
      toast({ 
        title: "Success", 
        description: "Smart monitoring suggestions generated!",
        duration: 3000
      });
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to generate monitoring suggestions",
        variant: "destructive"
      });
    } finally {
      setGeneratingImplementation(false);
    }
  };

  const handleOpenMonitoringDashboard = async (scenario) => {
    try {
      const response = await axios.get(`${API}/scenarios/${scenario.id}/monitoring-dashboard`);
      setMonitoringDashboard({
        ...monitoringDashboard,
        [scenario.id]: response.data
      });
      setShowMonitoringDialog(scenario);
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to load monitoring dashboard",
        variant: "destructive"
      });
    }
  };

  const handleAddMonitoringSource = async (scenario) => {
    setShowAddSourceDialog(scenario);
    setNewSourceData({
      source_type: '',
      source_url: '',
      source_name: '',  
      monitoring_frequency: 'daily',
      data_keywords: []
    });
  };

  const submitMonitoringSource = async () => {
    if (!showAddSourceDialog) return;
    
    try {
      const response = await axios.post(`${API}/scenarios/${showAddSourceDialog.id}/add-monitoring-source`, newSourceData);
      
      setMonitoringSources({
        ...monitoringSources,
        [showAddSourceDialog.id]: [
          ...(monitoringSources[showAddSourceDialog.id] || []),
          response.data
        ]
      });
      
      setShowAddSourceDialog(null);
      toast({ 
        title: "Success", 
        description: "Monitoring source added successfully!",
        duration: 3000
      });
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to add monitoring source",
        variant: "destructive"
      });
    }
  };

  const handleCollectData = async (scenario) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/scenarios/${scenario.id}/collect-data`);
      
      toast({ 
        title: "Data Collection Started", 
        description: `Collecting data from ${response.data.sources_monitored} monitoring sources`,
        duration: 4000
      });
      
      // Refresh monitoring dashboard
      setTimeout(() => handleOpenMonitoringDashboard(scenario), 2000);
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to start data collection",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeployMonitors = async (scenario) => {
    try {
      setDeployingMonitors(true);
      const response = await axios.post(`${API}/scenarios/${scenario.id}/deploy-monitors`);
      setMonitorAgents({
        ...monitorAgents,
        [scenario.id]: response.data
      });
      
      toast({ 
        title: "Success", 
        description: "AI Monitor Agents deployed successfully!",
        duration: 3000
      });
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to deploy monitor agents",
        variant: "destructive"
      });
    } finally {
      setDeployingMonitors(false);
    }
  };

  const handleComplexSystemsAnalysis = async (scenario) => {
    try {
      setGeneratingImplementation(true);
      const response = await axios.post(`${API}/scenarios/${scenario.id}/complex-systems-analysis`);
      setComplexSystems({
        ...complexSystems,
        [scenario.id]: response.data
      });
      
      setImplementationView({ scenario, type: 'complex-systems', data: response.data });
      
      toast({ 
        title: "Success", 
        description: "Complex Adaptive Systems analysis completed!",
        duration: 3000
      });
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to analyze complex systems",
        variant: "destructive"
      });
    } finally {
      setGeneratingImplementation(false);
    }
  };

  const handleGenerateMetrics = async (scenario) => {
    try {
      const response = await axios.post(`${API}/scenarios/${scenario.id}/generate-metrics`);
      setSystemMetrics({
        ...systemMetrics,
        [scenario.id]: response.data
      });
      
      toast({ 
        title: "Success", 
        description: "System metrics generated successfully!",
        duration: 3000
      });
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to generate system metrics",
        variant: "destructive"
      });
    }
  };

  const handleGenerateLearningInsights = async (scenario) => {
    try {
      setGeneratingImplementation(true);
      const response = await axios.post(`${API}/scenarios/${scenario.id}/generate-learning-insights`);
      setLearningInsights({
        ...learningInsights,
        [scenario.id]: response.data
      });
      
      setImplementationView({ scenario, type: 'learning-insights', data: response.data });
      
      toast({ 
        title: "Success", 
        description: "Adaptive learning insights generated!",
        duration: 3000
      });
      
    } catch (error) {
      toast({ 
        title: "Error", 
        description: "Failed to generate learning insights",
        variant: "destructive"
      });
    } finally {
      setGeneratingImplementation(false);
    }
  };

  const getCrisisTypeColor = (type) => {
    const colors = {
      'natural_disaster': 'bg-red-100 text-red-800',
      'economic_crisis': 'bg-yellow-100 text-yellow-800',
      'social_unrest': 'bg-purple-100 text-purple-800',
      'pandemic': 'bg-pink-100 text-pink-800',
      'cyber_attack': 'bg-blue-100 text-blue-800',
      'supply_chain_disruption': 'bg-orange-100 text-orange-800',
      'climate_change': 'bg-green-100 text-green-800',
      'political_instability': 'bg-gray-100 text-gray-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'bg-gray-100 text-gray-800',
      'active': 'bg-green-100 text-green-800',
      'completed': 'bg-blue-100 text-blue-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const filteredAndSortedScenarios = scenarios
    .filter(scenario => {
      if (filterStatus !== 'all' && scenario.status !== filterStatus) return false;
      if (filterType !== 'all' && scenario.crisis_type !== filterType) return false;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'created_at') return new Date(b.created_at) - new Date(a.created_at);
      if (sortBy === 'severity_level') return b.severity_level - a.severity_level;
      if (sortBy === 'title') return a.title.localeCompare(b.title);
      return 0;
    });

  const crisisTypes = [
    'natural_disaster',
    'economic_crisis', 
    'social_unrest',
    'pandemic',
    'cyber_attack',
    'supply_chain_disruption',
    'climate_change',
    'political_instability'
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Brain className="w-12 h-12 animate-pulse text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading scenarios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with filters */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Crisis Scenarios</h2>
          <p className="text-gray-600">Manage and analyze your crisis simulation scenarios</p>
        </div>
        
        <div className="flex flex-wrap gap-3">
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
            </SelectContent>
          </Select>

          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              {crisisTypes.map((type) => (
                <SelectItem key={type} value={type}>
                  {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="created_at">Date Created</SelectItem>
              <SelectItem value="severity_level">Severity</SelectItem>
              <SelectItem value="title">Title</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Scenarios grid */}
      {filteredAndSortedScenarios.length === 0 ? (
        <div className="text-center py-12">
          <Globe className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No scenarios found</h3>
          <p className="text-gray-600 mb-4">
            {scenarios.length === 0 
              ? "Create your first crisis scenario to get started"
              : "No scenarios match your current filters"
            }
          </p>
          {scenarios.length === 0 && (
            <Button onClick={() => window.location.hash = '#create'} className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Create First Scenario
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredAndSortedScenarios.map((scenario) => (
            <Card key={scenario.id} className="hover:shadow-lg transition-shadow duration-200">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg leading-tight">{scenario.title}</CardTitle>
                  <div className="flex gap-1">
                    <Badge className={getStatusColor(scenario.status)} variant="secondary">
                      {scenario.status}
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Badge className={getCrisisTypeColor(scenario.crisis_type)} variant="outline">
                    {scenario.crisis_type.replace('_', ' ')}
                  </Badge>
                  <Badge variant="outline" className="bg-red-50 text-red-700">
                    Severity {scenario.severity_level}/10
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent className="pt-0">
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {scenario.description}
                </p>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Globe className="w-3 h-3" />
                    <span>Regions: {scenario.affected_regions.slice(0, 2).join(', ')}</span>
                    {scenario.affected_regions.length > 2 && (
                      <span>+{scenario.affected_regions.length - 2} more</span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Variables: {scenario.key_variables.length}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>Created: {new Date(scenario.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedScenario(scenario)}
                      className="flex-1"
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      View
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRunSimulation(scenario)}
                      disabled={loading}
                      className="flex-1"
                    >
                      <Play className="w-3 h-3 mr-1" />
                      Simulate
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setScenarioToDelete(scenario);
                        setShowDeleteDialog(true);
                      }}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <AlertTriangle className="w-3 h-3" />
                    </Button>
                  </div>
                  
                  <div className="space-y-1">
                    <div className="flex gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleGenerateImplementation(scenario, 'game-book')}
                        disabled={generatingImplementation}
                        className="flex-1 text-xs py-1"
                      >
                        <BookOpen className="w-3 h-3 mr-1" />
                        Game Book
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleGenerateImplementation(scenario, 'action-plan')}
                        disabled={generatingImplementation}
                        className="flex-1 text-xs py-1"
                      >
                        <CheckSquare className="w-3 h-3 mr-1" />
                        Actions
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleGenerateImplementation(scenario, 'strategy-implementation')}
                        disabled={generatingImplementation}
                        className="flex-1 text-xs py-1"
                      >
                        <Target className="w-3 h-3 mr-1" />
                        Strategy
                      </Button>
                    </div>
                    
                    <div className="flex gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeployMonitors(scenario)}
                        disabled={deployingMonitors}
                        className="flex-1 text-xs py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200"
                      >
                        <Monitor className="w-3 h-3 mr-1" />
                        AI Monitors
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleComplexSystemsAnalysis(scenario)}
                        disabled={generatingImplementation}
                        className="flex-1 text-xs py-1 bg-purple-50 hover:bg-purple-100 text-purple-700 border-purple-200"
                      >
                        <Network className="w-3 h-3 mr-1" />
                        Complex Systems
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleGenerateLearningInsights(scenario)}
                        disabled={generatingImplementation}
                        className="flex-1 text-xs py-1 bg-green-50 hover:bg-green-100 text-green-700 border-green-200"
                      >
                        <Brain className="w-3 h-3 mr-1" />
                        AI Learning
                      </Button>
                    </div>
                    
                    <div className="flex gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSuggestMonitoringSources(scenario)}
                        disabled={generatingImplementation}
                        className="flex-1 text-xs py-1 bg-yellow-50 hover:bg-yellow-100 text-yellow-700 border-yellow-200"
                      >
                        <Lightbulb className="w-3 h-3 mr-1" />
                        Smart Sources
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAddMonitoringSource(scenario)}
                        className="flex-1 text-xs py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border-indigo-200"
                      >
                        <Link className="w-3 h-3 mr-1" />
                        Add Sources
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleOpenMonitoringDashboard(scenario)}
                        className="flex-1 text-xs py-1 bg-teal-50 hover:bg-teal-100 text-teal-700 border-teal-200"
                      >
                        <Cloud className="w-3 h-3 mr-1" />
                        Dashboard
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Scenario Detail Dialog */}
      {selectedScenario && (
        <Dialog open={!!selectedScenario} onOpenChange={() => setSelectedScenario(null)}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                {selectedScenario.title}
              </DialogTitle>
              <DialogDescription>
                <div className="flex gap-2 mt-2">
                  <Badge className={getCrisisTypeColor(selectedScenario.crisis_type)}>
                    {selectedScenario.crisis_type.replace('_', ' ')}
                  </Badge>
                  <Badge className={getStatusColor(selectedScenario.status)}>
                    {selectedScenario.status}
                  </Badge>
                  <Badge variant="outline">
                    Severity {selectedScenario.severity_level}/10
                  </Badge>
                </div>
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Description</h4>
                <p className="text-gray-700">{selectedScenario.description}</p>
              </div>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Affected Regions</h4>
                  <div className="space-y-1">
                    {selectedScenario.affected_regions.map((region, index) => (
                      <Badge key={index} variant="outline" className="mr-2 mb-1">
                        {region}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Key Variables</h4>
                  <div className="space-y-1">
                    {selectedScenario.key_variables.map((variable, index) => (
                      <Badge key={index} variant="outline" className="mr-2 mb-1">
                        {variable}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Created:</span> {new Date(selectedScenario.created_at).toLocaleString()}
                </div>
                <div>
                  <span className="font-medium">Last Updated:</span> {new Date(selectedScenario.updated_at).toLocaleString()}
                </div>
              </div>

              {selectedScenario.simulation_result && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Latest Simulation Results</h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-700 mb-2">
                      <span className="font-medium">Analysis:</span> {selectedScenario.simulation_result.analysis?.substring(0, 200)}...
                    </p>
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Confidence Score:</span> {(selectedScenario.simulation_result.confidence_score * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <Button onClick={() => handleRunSimulation(selectedScenario)} disabled={loading} className="flex-1">
                  <Play className="w-4 h-4 mr-2" />
                  Run New Simulation
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    onScenarioSelect(selectedScenario);
                    setSelectedScenario(null);
                  }}
                  className="flex-1"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Chat with AI Genie
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Delete Confirmation Dialog */}
      {showDeleteDialog && scenarioToDelete && (
        <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Scenario</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete "{scenarioToDelete.title}"? This action cannot be undone.
              </DialogDescription>
            </DialogHeader>
            <div className="flex gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowDeleteDialog(false)} className="flex-1">
                Cancel
              </Button>
              <Button 
                variant="destructive" 
                onClick={() => handleDeleteScenario(scenarioToDelete.id)}
                className="flex-1"
              >
                Delete Scenario
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Monitoring Dashboard Dialog */}
      {showMonitoringDialog && monitoringDashboard[showMonitoringDialog.id] && (
        <Dialog open={!!showMonitoringDialog} onOpenChange={() => setShowMonitoringDialog(null)}>
          <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Cloud className="w-5 h-5 text-teal-600" />
                Intelligent Monitoring Network - {showMonitoringDialog.title}
              </DialogTitle>
              <DialogDescription>
                Real-time data collection and AI-powered analysis from collaborative team sources
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              {/* Monitoring Summary */}
              <div className="grid md:grid-cols-4 gap-4">
                <Card className="bg-blue-50 border-blue-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-blue-600 font-medium">Active Sources</p>
                        <p className="text-2xl font-bold text-blue-900">
                          {monitoringDashboard[showMonitoringDialog.id].monitoring_summary.active_sources}
                        </p>
                      </div>
                      <Database className="w-8 h-8 text-blue-500" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="bg-green-50 border-green-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-green-600 font-medium">Data Points</p>
                        <p className="text-2xl font-bold text-green-900">
                          {monitoringDashboard[showMonitoringDialog.id].monitoring_summary.total_data_points}
                        </p>
                      </div>
                      <BarChart3 className="w-8 h-8 text-green-500" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="bg-purple-50 border-purple-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-purple-600 font-medium">Avg Relevance</p>
                        <p className="text-2xl font-bold text-purple-900">
                          {Math.round(monitoringDashboard[showMonitoringDialog.id].monitoring_summary.average_relevance_score * 100)}%
                        </p>
                      </div>
                      <Target className="w-8 h-8 text-purple-500" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="bg-orange-50 border-orange-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-orange-600 font-medium">Suggestions</p>
                        <p className="text-2xl font-bold text-orange-900">
                          {monitoringDashboard[showMonitoringDialog.id].smart_suggestions_count}
                        </p>
                      </div>
                      <Lightbulb className="w-8 h-8 text-orange-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Monitoring Sources */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Link className="w-5 h-5" />
                    Team Monitoring Sources
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {monitoringDashboard[showMonitoringDialog.id].monitoring_sources.length === 0 ? (
                      <div className="text-center py-6 text-gray-500">
                        <Link className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>No monitoring sources added yet.</p>
                        <Button 
                          onClick={() => handleAddMonitoringSource(showMonitoringDialog)}
                          className="mt-3"
                          size="sm"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Add First Source
                        </Button>
                      </div>
                    ) : (
                      monitoringDashboard[showMonitoringDialog.id].monitoring_sources.map((source, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${
                              source.status === 'active' ? 'bg-green-500' : 
                              source.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
                            }`}></div>
                            <div>
                              <p className="font-medium text-gray-900">{source.name}</p>
                              <p className="text-sm text-gray-600">{source.type.replace('_', ' ')}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-right">
                              <p className="text-sm font-medium">{Math.round(source.relevance_score * 100)}% relevance</p>
                              <p className="text-xs text-gray-500">{source.data_points} data points</p>
                            </div>
                            <Badge variant={source.status === 'active' ? 'default' : 'secondary'}>
                              {source.status}
                            </Badge>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Insights */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Rss className="w-5 h-5" />
                    Recent AI Insights
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {monitoringDashboard[showMonitoringDialog.id].recent_insights.length === 0 ? (
                      <div className="text-center py-6 text-gray-500">
                        <Rss className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>No data collected yet.</p>
                        <Button 
                          onClick={() => handleCollectData(showMonitoringDialog)}
                          className="mt-3"
                          size="sm"
                        >
                          <Activity className="w-4 h-4 mr-2" />
                          Start Data Collection
                        </Button>
                      </div>
                    ) : (
                      monitoringDashboard[showMonitoringDialog.id].recent_insights.map((insight, idx) => (
                        <div key={idx} className="p-3 border rounded-lg">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-medium text-gray-900">{insight.title}</h4>
                            <div className="flex items-center gap-2">
                              <Badge variant={
                                insight.urgency === 'critical' ? 'destructive' :
                                insight.urgency === 'high' ? 'default' :
                                insight.urgency === 'medium' ? 'secondary' : 'outline'
                              }>
                                {insight.urgency}
                              </Badge>
                              <span className="text-xs text-gray-500">
                                {Math.round(insight.relevance * 100)}% relevant
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-gray-700">{insight.summary}</p>
                          <p className="text-xs text-gray-500 mt-2">
                            {new Date(insight.collected_at).toLocaleString()}
                          </p>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>

              <div className="flex gap-3 pt-4">
                <Button onClick={() => handleCollectData(showMonitoringDialog)} className="flex-1">
                  <Activity className="w-4 h-4 mr-2" />
                  Collect New Data
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => handleAddMonitoringSource(showMonitoringDialog)}
                  className="flex-1"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Monitoring Source
                </Button>
                <Button variant="outline" onClick={() => setShowMonitoringDialog(null)}>
                  Close
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Add Monitoring Source Dialog */}
      {showAddSourceDialog && (
        <Dialog open={!!showAddSourceDialog} onOpenChange={() => setShowAddSourceDialog(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Link className="w-5 h-5 text-indigo-600" />
                Add Monitoring Source - {showAddSourceDialog.title}
              </DialogTitle>
              <DialogDescription>
                Add a new data source for AI monitors to track and analyze
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="source_type">Source Type</Label>
                <Select value={newSourceData.source_type} onValueChange={(value) => setNewSourceData({...newSourceData, source_type: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select source type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="news_api">News API</SelectItem>
                    <SelectItem value="social_media">Social Media</SelectItem>
                    <SelectItem value="government_data">Government Data</SelectItem>
                    <SelectItem value="weather_api">Weather API</SelectItem>
                    <SelectItem value="financial_market">Financial Market</SelectItem>
                    <SelectItem value="custom_url">Custom URL</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="source_name">Source Name</Label>
                <Input
                  id="source_name"
                  value={newSourceData.source_name}
                  onChange={(e) => setNewSourceData({...newSourceData, source_name: e.target.value})}
                  placeholder="e.g., USGS Earthquake Feed"
                  required
                />
              </div>

              <div>
                <Label htmlFor="source_url">Source URL</Label>
                <Input
                  id="source_url"
                  type="url"
                  value={newSourceData.source_url}
                  onChange={(e) => setNewSourceData({...newSourceData, source_url: e.target.value})}
                  placeholder="https://example.com/api/data"
                  required
                />
              </div>

              <div>
                <Label htmlFor="monitoring_frequency">Monitoring Frequency</Label>
                <Select value={newSourceData.monitoring_frequency} onValueChange={(value) => setNewSourceData({...newSourceData, monitoring_frequency: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="real_time">Real-time</SelectItem>
                    <SelectItem value="hourly">Hourly</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Monitoring Keywords</Label>
                <div className="flex gap-2 mb-2">
                  <Input
                    placeholder="Add keyword (e.g., emergency, crisis)"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.target.value.trim()) {
                        setNewSourceData({
                          ...newSourceData,
                          data_keywords: [...newSourceData.data_keywords, e.target.value.trim()]
                        });
                        e.target.value = '';
                      }
                    }}
                  />
                  <Button type="button" size="sm" variant="outline">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {newSourceData.data_keywords.map((keyword, idx) => (
                    <Badge 
                      key={idx} 
                      variant="secondary" 
                      className="cursor-pointer"
                      onClick={() => setNewSourceData({
                        ...newSourceData,
                        data_keywords: newSourceData.data_keywords.filter((_, i) => i !== idx)
                      })}
                    >
                      {keyword} ×
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <Button onClick={submitMonitoringSource} className="flex-1">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Monitoring Source
                </Button>
                <Button variant="outline" onClick={() => setShowAddSourceDialog(null)}>
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Implementation View Dialog */}
      {implementationView && (
        <Dialog open={!!implementationView} onOpenChange={() => setImplementationView(null)}>
          <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                {implementationView.type === 'game-book' && <BookOpen className="w-5 h-5 text-blue-600" />}
                {implementationView.type === 'action-plan' && <CheckSquare className="w-5 h-5 text-green-600" />}
                {implementationView.type === 'strategy-implementation' && <Target className="w-5 h-5 text-purple-600" />}
                {implementationView.type.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())} - {implementationView.scenario.title}
              </DialogTitle>
              <DialogDescription>
                Strategic implementation guidance for crisis scenario management
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              {implementationView.type === 'monitoring-suggestions' && (
                <div className="space-y-6">
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-yellow-900 mb-3 flex items-center gap-2">
                      <Lightbulb className="w-4 h-4" />
                      Smart Monitoring Source Suggestions
                    </h4>
                    <p className="text-sm text-yellow-800">
                      AI-generated suggestions for optimal data sources and monitoring strategies based on your scenario.
                    </p>
                  </div>
                  
                  <div className="space-y-4">
                    {implementationView.data.map((suggestion, idx) => (
                      <div key={idx} className="border rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="font-semibold text-gray-900 flex items-center gap-2">
                            {suggestion.suggestion_type === 'data_source' && <Database className="w-4 h-4 text-blue-600" />}
                            {suggestion.suggestion_type === 'monitoring_keyword' && <Rss className="w-4 h-4 text-green-600" />}
                            {suggestion.suggestion_type === 'analysis_focus' && <Target className="w-4 h-4 text-purple-600" />}
                            {suggestion.suggestion_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </h5>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {Math.round(suggestion.confidence_score * 100)}% confidence
                            </Badge>
                            {suggestion.suggestion_content.includes('http') && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => window.open(suggestion.suggestion_content.match(/https?:\/\/[^\s]+/)?.[0], '_blank')}
                              >
                                <ExternalLink className="w-3 h-3" />
                              </Button>
                            )}
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 mb-2">{suggestion.suggestion_content}</p>
                        <p className="text-xs text-gray-600 mb-3">{suggestion.reasoning}</p>
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="text-xs"
                            onClick={() => {
                              // Auto-fill add source dialog with suggestion data
                              if (suggestion.suggestion_type === 'data_source') {
                                const urlMatch = suggestion.suggestion_content.match(/https?:\/\/[^\s]+/);
                                if (urlMatch) {
                                  setNewSourceData({
                                    source_type: 'custom_url',
                                    source_url: urlMatch[0],
                                    source_name: suggestion.suggestion_content.split(' - ')[0] || 'Suggested Source',
                                    monitoring_frequency: 'daily',
                                    data_keywords: implementationView.scenario.key_variables.slice(0, 3)
                                  });
                                  setShowAddSourceDialog(implementationView.scenario);
                                  setImplementationView(null);
                                }
                              }
                              toast({ title: "Suggestion Applied", description: "Source suggestion has been prepared for addition." });
                            }}
                          >
                            <Plus className="w-3 h-3 mr-1" />
                            Use This Suggestion
                          </Button>
                          {!suggestion.implemented && (
                            <Badge variant="secondary" className="text-xs">
                              New
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h5 className="font-semibold text-blue-900 mb-2">Next Steps</h5>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>• Click "Use This Suggestion" to quickly add recommended sources</li>
                      <li>• Customize monitoring frequency based on your needs</li>
                      <li>• Add team members to collaborate on monitoring sources</li>
                      <li>• Set up automated data collection for continuous insights</li>
                    </ul>
                  </div>
                </div>
              )}

              {implementationView.type === 'complex-systems' && (
                <div className="space-y-6">
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-purple-900 mb-3 flex items-center gap-2">
                      <Network className="w-4 h-4" />
                      Complex Adaptive Systems Analysis
                    </h4>
                    <div className="text-sm text-purple-800 whitespace-pre-line max-h-60 overflow-y-auto">
                      {implementationView.data.system_dynamics}
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">System Components</h5>
                      <ul className="text-sm text-gray-700 space-y-1 max-h-32 overflow-y-auto">
                        {implementationView.data.system_components.map((component, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Layers className="w-3 h-3 mt-0.5 text-blue-600" />
                            {component}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Interconnections</h5>
                      <ul className="text-sm text-gray-700 space-y-1 max-h-32 overflow-y-auto">
                        {implementationView.data.interconnections.map((connection, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Network className="w-3 h-3 mt-0.5 text-purple-600" />
                            {connection}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Feedback Loops</h5>
                      <ul className="text-sm text-gray-700 space-y-1 max-h-32 overflow-y-auto">
                        {implementationView.data.feedback_loops.map((loop, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <TrendingUp className="w-3 h-3 mt-0.5 text-green-600" />
                            {loop}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Emergent Behaviors</h5>
                      <ul className="text-sm text-gray-700 space-y-1 max-h-32 overflow-y-auto">
                        {implementationView.data.emergent_behaviors.map((behavior, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Zap className="w-3 h-3 mt-0.5 text-yellow-600" />
                            {behavior}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Adaptation Mechanisms</h5>
                      <ul className="text-sm text-gray-700 space-y-1 max-h-32 overflow-y-auto">
                        {implementationView.data.adaptation_mechanisms.map((mechanism, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Cpu className="w-3 h-3 mt-0.5 text-blue-600" />
                            {mechanism}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Critical Tipping Points</h5>
                      <ul className="text-sm text-gray-700 space-y-1 max-h-32 overflow-y-auto">
                        {implementationView.data.tipping_points.map((point, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <AlertTriangle className="w-3 h-3 mt-0.5 text-red-600" />
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {implementationView.type === 'learning-insights' && (
                <div className="space-y-6">
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
                      <Brain className="w-4 h-4" />
                      Adaptive Learning Insights
                    </h4>
                    <p className="text-sm text-green-800">
                      AI-powered insights generated from your scenario interactions and patterns.
                    </p>
                  </div>
                  
                  <div className="space-y-4">
                    {implementationView.data.map((insight, idx) => (
                      <div key={idx} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="font-semibold text-gray-900 flex items-center gap-2">
                            {insight.insight_type === 'pattern_recognition' && <BarChart3 className="w-4 h-4 text-blue-600" />}
                            {insight.insight_type === 'outcome_prediction' && <TrendingUp className="w-4 h-4 text-green-600" />}
                            {insight.insight_type === 'optimization_suggestion' && <Target className="w-4 h-4 text-purple-600" />}
                            {insight.insight_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </h5>
                          <Badge variant="outline" className="text-xs">
                            {Math.round(insight.confidence_score * 100)}% confidence
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-700">{insight.insight_content}</p>
                        <div className="mt-2 flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="text-xs"
                            onClick={() => {
                              // Mark insight as applied
                              toast({ title: "Insight Applied", description: "This insight has been marked as applied to your strategy." });
                            }}
                          >
                            Apply Insight
                          </Button>
                          {!insight.applied && (
                            <Badge variant="secondary" className="text-xs">
                              New
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {implementationView.type === 'game-book' && (
                <div className="space-y-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                      <BookOpen className="w-4 h-4" />
                      Crisis Game Book Content
                    </h4>
                    <div className="text-sm text-blue-800 whitespace-pre-line max-h-60 overflow-y-auto">
                      {implementationView.data.game_book_content}
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Critical Decision Points</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.decision_points.map((point, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <CheckSquare className="w-3 h-3 mt-0.5 text-green-600" />
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Resource Requirements</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.resource_requirements.map((resource, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Shield className="w-3 h-3 mt-0.5 text-orange-600" />
                            {resource}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Timeline Phases</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.timeline_phases.map((phase, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <TrendingUp className="w-3 h-3 mt-0.5 text-blue-600" />
                            {phase}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Success Metrics</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.success_metrics.map((metric, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Target className="w-3 h-3 mt-0.5 text-purple-600" />
                            {metric}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {implementationView.type === 'action-plan' && (
                <div className="space-y-6">
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="bg-red-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-red-900 mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Immediate Actions (0-24h)
                      </h5>
                      <ul className="text-sm text-red-800 space-y-1">
                        {implementationView.data.immediate_actions.map((action, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <CheckSquare className="w-3 h-3 mt-0.5" />
                            {action}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4" />
                        Short-term Actions (1-30d)
                      </h5>
                      <ul className="text-sm text-yellow-800 space-y-1">
                        {implementationView.data.short_term_actions.map((action, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <CheckSquare className="w-3 h-3 mt-0.5" />
                            {action}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-green-900 mb-2 flex items-center gap-2">
                        <Target className="w-4 h-4" />
                        Long-term Actions (1-12m)
                      </h5>
                      <ul className="text-sm text-green-800 space-y-1">
                        {implementationView.data.long_term_actions.map((action, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <CheckSquare className="w-3 h-3 mt-0.5" />
                            {action}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Responsible Parties</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.responsible_parties.map((party, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Users className="w-3 h-3 mt-0.5 text-blue-600" />
                            {party}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Resource Allocation</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.resource_allocation.map((resource, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Shield className="w-3 h-3 mt-0.5 text-green-600" />
                            {resource}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h5 className="font-semibold text-blue-900 mb-2">Priority Level</h5>
                    <Badge className={`${implementationView.data.priority_level === 'HIGH' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {implementationView.data.priority_level} PRIORITY
                    </Badge>
                  </div>
                </div>
              )}

              {implementationView.type === 'strategy-implementation' && (
                <div className="space-y-6">
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-purple-900 mb-3 flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      Strategic Implementation Framework
                    </h4>
                    <div className="text-sm text-purple-800 whitespace-pre-line max-h-60 overflow-y-auto">
                      {implementationView.data.implementation_strategy}
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Organizational Changes</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.organizational_changes.map((change, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Users className="w-3 h-3 mt-0.5 text-blue-600" />
                            {change}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Policy Recommendations</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.policy_recommendations.map((policy, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <FileText className="w-3 h-3 mt-0.5 text-green-600" />
                            {policy}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Training Requirements</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.training_requirements.map((training, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Brain className="w-3 h-3 mt-0.5 text-purple-600" />
                            {training}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h5 className="font-semibold text-gray-900 mb-2">Budget Considerations</h5>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {implementationView.data.budget_considerations.map((budget, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <TrendingUp className="w-3 h-3 mt-0.5 text-orange-600" />
                            {budget}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h5 className="font-semibold text-gray-900 mb-2">Stakeholder Engagement</h5>
                    <ul className="text-sm text-gray-700 space-y-1">
                      {implementationView.data.stakeholder_engagement.map((engagement, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <Users className="w-3 h-3 mt-0.5 text-indigo-600" />
                          {engagement}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-4 border-t">
                <Button 
                  onClick={() => {
                    // Create downloadable content
                    const content = JSON.stringify(implementationView.data, null, 2);
                    const blob = new Blob([content], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${implementationView.type}-${implementationView.scenario.title}.json`;
                    a.click();
                  }}
                  className="flex-1"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download {implementationView.type.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </Button>
                <Button variant="outline" onClick={() => setImplementationView(null)} className="flex-1">
                  Close
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

// Company Management Component
const CompanyManagement = () => {
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateCompany, setShowCreateCompany] = useState(false);
  const [companyData, setCompanyData] = useState({
    company_name: '',
    industry: '',
    company_size: 'medium',
    website_url: '',
    description: '',
    location: ''
  });

  useEffect(() => {
    fetchCompanyData();
  }, []);

  const fetchCompanyData = async () => {
    try {
      // Try to get user's company if they have one
      const userResponse = await axios.get(`${API}/me`);
      if (userResponse.data.company_id) {
        const companyResponse = await axios.get(`${API}/companies/${userResponse.data.company_id}`);
        setCompany(companyResponse.data);
      }
    } catch (error) {
      console.error('Failed to fetch company data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCompany = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/companies`, companyData);
      setCompany(response.data);
      setShowCreateCompany(false);
      toast({ title: "Success", description: "Company created successfully!" });
    } catch (error) {
      toast({ 
        title: "Error", 
        description: error.response?.data?.detail || "Failed to create company",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Building2 className="w-12 h-12 animate-pulse text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading company information...</p>
        </div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2 text-2xl">
              <Building2 className="w-8 h-8 text-blue-600" />
              Enterprise Setup
            </CardTitle>
            <CardDescription>
              Set up your company profile to unlock advanced crisis management features
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!showCreateCompany ? (
              <div className="text-center py-8">
                <Building2 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Company Profile</h3>
                <p className="text-gray-600 mb-6">
                  Create your company profile to access advanced features like document analysis, 
                  team collaboration, and company-specific crisis scenarios.
                </p>
                <Button onClick={() => setShowCreateCompany(true)} className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Company Profile
                </Button>
              </div>
            ) : (
              <form onSubmit={handleCreateCompany} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="company_name">Company Name</Label>
                    <Input
                      id="company_name"
                      value={companyData.company_name}
                      onChange={(e) => setCompanyData({...companyData, company_name: e.target.value})}
                      placeholder="Your company name"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="industry">Industry</Label>
                    <Select value={companyData.industry} onValueChange={(value) => setCompanyData({...companyData, industry: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select industry" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="technology">Technology</SelectItem>
                        <SelectItem value="healthcare">Healthcare</SelectItem>
                        <SelectItem value="finance">Finance</SelectItem>
                        <SelectItem value="manufacturing">Manufacturing</SelectItem>
                        <SelectItem value="retail">Retail</SelectItem>
                        <SelectItem value="energy">Energy</SelectItem>
                        <SelectItem value="transportation">Transportation</SelectItem>
                        <SelectItem value="government">Government</SelectItem>
                        <SelectItem value="education">Education</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="company_size">Company Size</Label>
                    <Select value={companyData.company_size} onValueChange={(value) => setCompanyData({...companyData, company_size: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="startup">Startup (1-10 employees)</SelectItem>
                        <SelectItem value="small">Small (11-50 employees)</SelectItem>
                        <SelectItem value="medium">Medium (51-200 employees)</SelectItem>
                        <SelectItem value="large">Large (201-1000 employees)</SelectItem>
                        <SelectItem value="enterprise">Enterprise (1000+ employees)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={companyData.location}
                      onChange={(e) => setCompanyData({...companyData, location: e.target.value})}
                      placeholder="City, Country"
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="website_url">Company Website (optional)</Label>
                  <Input
                    id="website_url"
                    type="url"
                    value={companyData.website_url}
                    onChange={(e) => setCompanyData({...companyData, website_url: e.target.value})}
                    placeholder="https://yourcompany.com"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    We'll analyze your website to suggest relevant crisis scenarios
                  </p>
                </div>

                <div>
                  <Label htmlFor="description">Company Description</Label>
                  <Textarea
                    id="description"
                    value={companyData.description}
                    onChange={(e) => setCompanyData({...companyData, description: e.target.value})}
                    placeholder="Brief description of your company's business..."
                    rows={4}
                    required
                  />
                </div>

                <div className="flex gap-3">
                  <Button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 flex-1">
                    {loading ? 'Creating...' : 'Create Company Profile'}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowCreateCompany(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Company Overview */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="w-6 h-6 text-blue-600" />
            {company.company_name}
          </CardTitle>
          <CardDescription>
            {company.industry} • {company.company_size} • {company.location}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 mb-4">{company.description}</p>
          {company.website_url && (
            <div className="flex items-center gap-2">
              <ExternalLink className="w-4 h-4 text-blue-600" />
              <a href={company.website_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                {company.website_url}
              </a>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Website Analysis */}
      {company.website_analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-600" />
              AI Website Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-purple-800 whitespace-pre-line">
                {company.website_analysis.substring(0, 500)}...
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-4 mt-4">
              <div className="bg-gray-50 p-3 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Key Assets</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {company.key_assets.slice(0, 3).map((asset, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <Shield className="w-3 h-3 mt-0.5 text-green-600" />
                      {asset}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Vulnerabilities</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {company.vulnerabilities.slice(0, 3).map((vuln, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <AlertTriangle className="w-3 h-3 mt-0.5 text-red-600" />
                      {vuln}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Stakeholders</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {company.stakeholders.slice(0, 3).map((stakeholder, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <Users className="w-3 h-3 mt-0.5 text-blue-600" />
                      {stakeholder}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6 text-center">
            <Upload className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Upload Documents</h3>
            <p className="text-sm text-gray-600">Business plans & strategy docs</p>
          </CardContent>
        </Card>
        
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6 text-center">
            <Users2 className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Manage Teams</h3>
            <p className="text-sm text-gray-600">Create crisis response teams</p>
          </CardContent>
        </Card>
        
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6 text-center">
            <Zap className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Rapid Analysis</h3>
            <p className="text-sm text-gray-600">AI-powered business insights</p>
          </CardContent>
        </Card>
        
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6 text-center">
            <BarChart className="w-8 h-8 text-orange-600 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Company Scenarios</h3>
            <p className="text-sm text-gray-600">Tailored crisis scenarios</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Document Management Component
const DocumentManagement = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadData, setUploadData] = useState({
    document_name: '',
    document_type: 'business_plan',
    document_content: ''
  });

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const userResponse = await axios.get(`${API}/me`);
      if (userResponse.data.company_id) {
        const response = await axios.get(`${API}/companies/${userResponse.data.company_id}/documents`);
        setDocuments(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadDocument = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const userResponse = await axios.get(`${API}/me`);
      const response = await axios.post(`${API}/companies/${userResponse.data.company_id}/documents`, uploadData);
      setDocuments([...documents, response.data]);
      setShowUploadDialog(false);
      setUploadData({ document_name: '', document_type: 'business_plan', document_content: '' });
      toast({ title: "Success", description: "Document uploaded and analyzed successfully!" });
    } catch (error) {
      toast({ 
        title: "Error", 
        description: error.response?.data?.detail || "Failed to upload document",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Document Intelligence</h2>
          <p className="text-gray-600">Upload and analyze business documents with AI insights</p>
        </div>
        <Button onClick={() => setShowUploadDialog(true)} className="bg-blue-600 hover:bg-blue-700">
          <Upload className="w-4 h-4 mr-2" />
          Upload Document
        </Button>
      </div>

      {/* Document Grid */}
      <div className="grid gap-6">
        {documents.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Documents Uploaded</h3>
            <p className="text-gray-600 mb-4">
              Upload business plans, market strategies, and operational documents for AI analysis
            </p>
            <Button onClick={() => setShowUploadDialog(true)} className="bg-blue-600 hover:bg-blue-700">
              <Upload className="w-4 h-4 mr-2" />
              Upload First Document
            </Button>
          </div>
        ) : (
          documents.map((doc) => (
            <Card key={doc.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  {doc.document_name}
                </CardTitle>
                <CardDescription>
                  <Badge variant="outline" className="mr-2">
                    {doc.document_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </Badge>
                  <span className="text-sm text-gray-500">
                    Uploaded {new Date(doc.created_at).toLocaleDateString()}
                  </span>
                </CardDescription>
              </CardHeader>
              <CardContent>
                {doc.ai_analysis && (
                  <div className="bg-blue-50 p-4 rounded-lg mb-4">
                    <h4 className="font-semibold text-blue-900 mb-2">AI Analysis</h4>
                    <p className="text-sm text-blue-800">
                      {doc.ai_analysis.substring(0, 300)}...
                    </p>
                  </div>
                )}
                
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <h5 className="font-semibold text-gray-900 mb-2">Key Insights</h5>
                    <ul className="text-sm text-gray-700 space-y-1">
                      {doc.key_insights.slice(0, 2).map((insight, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <Lightbulb className="w-3 h-3 mt-0.5 text-yellow-600" />
                          {insight.substring(0, 50)}...
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <h5 className="font-semibold text-gray-900 mb-2">Risk Factors</h5>
                    <ul className="text-sm text-gray-700 space-y-1">
                      {doc.risk_factors.slice(0, 2).map((risk, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <AlertTriangle className="w-3 h-3 mt-0.5 text-red-600" />
                          {risk.substring(0, 50)}...
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <h5 className="font-semibold text-gray-900 mb-2">Strategic Priorities</h5>
                    <ul className="text-sm text-gray-700 space-y-1">
                      {doc.strategic_priorities.slice(0, 2).map((priority, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <Target className="w-3 h-3 mt-0.5 text-purple-600" />
                          {priority.substring(0, 50)}...
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Upload Dialog */}
      {showUploadDialog && (
        <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5 text-blue-600" />
                Upload Business Document
              </DialogTitle>
              <DialogDescription>
                Upload business plans, strategies, or operational documents for AI analysis
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleUploadDocument} className="space-y-4">
              <div>
                <Label htmlFor="document_name">Document Name</Label>
                <Input
                  id="document_name"
                  value={uploadData.document_name}
                  onChange={(e) => setUploadData({...uploadData, document_name: e.target.value})}
                  placeholder="e.g., Business Plan 2024"
                  required
                />
              </div>

              <div>
                <Label htmlFor="document_type">Document Type</Label>
                <Select value={uploadData.document_type} onValueChange={(value) => setUploadData({...uploadData, document_type: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="business_plan">Business Plan</SelectItem>
                    <SelectItem value="market_strategy">Market Strategy</SelectItem>
                    <SelectItem value="financial_report">Financial Report</SelectItem>
                    <SelectItem value="operational_plan">Operational Plan</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="document_content">Document Content</Label>
                <Textarea
                  id="document_content"
                  value={uploadData.document_content}
                  onChange={(e) => setUploadData({...uploadData, document_content: e.target.value})}
                  placeholder="Paste your document content here..."
                  rows={10}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Paste the text content of your document for AI analysis
                </p>
              </div>

              <div className="flex gap-3 pt-4">
                <Button type="submit" disabled={loading} className="flex-1">
                  {loading ? 'Analyzing...' : 'Upload & Analyze Document'}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowUploadDialog(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

// Main App Component
const AppContent = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);

  const handleScenarioCreated = (newScenario) => {
    setScenarios([...scenarios, newScenario]);
    setActiveTab('scenarios');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <Brain className="w-8 h-8 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">Polycrisis Simulator</h1>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-600">
                Welcome, <span className="font-semibold">{user?.username}</span>
              </div>
              <Button variant="outline" size="sm" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="h-12 bg-transparent">
              <TabsTrigger value="dashboard" className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Dashboard
              </TabsTrigger>
              <TabsTrigger value="create" className="flex items-center gap-2">
                <Plus className="w-4 h-4" />
                Create Scenario
              </TabsTrigger>
              <TabsTrigger value="scenarios" className="flex items-center gap-2">
                <Globe className="w-4 h-4" />
                Scenarios
              </TabsTrigger>
              <TabsTrigger value="ai-genie" className="flex items-center gap-2">
                <Brain className="w-4 h-4" />
                AI Genie
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsContent value="dashboard">
            <AdvancedDashboard />
          </TabsContent>
          
          <TabsContent value="create">
            <ScenarioCreator onScenarioCreated={handleScenarioCreated} />
          </TabsContent>
          
          <TabsContent value="scenarios">
            <ScenarioManagement onScenarioSelect={setSelectedScenario} />
          </TabsContent>
          
          <TabsContent value="ai-genie">
            <AIGenie selectedScenario={selectedScenario} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/*" element={<AuthRoutes />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </div>
    </AuthProvider>
  );
}

const AuthRoutes = () => {
  const { isAuthenticated } = useAuth();
  
  return isAuthenticated ? <AppContent /> : <AuthPage />;
};

export default App;