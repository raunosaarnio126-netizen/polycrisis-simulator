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
import { AlertTriangle, Brain, Globe, Shield, TrendingUp, Users, Plus, Play, Eye, MessageSquare } from 'lucide-react';

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
    organization: ''
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

// Dashboard Components
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
        </div>
        
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
            <Dashboard />
          </TabsContent>
          
          <TabsContent value="create">
            <ScenarioCreator onScenarioCreated={handleScenarioCreated} />
          </TabsContent>
          
          <TabsContent value="scenarios">
            <div className="text-center py-8 text-gray-500">
              <Globe className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Scenario management interface coming soon...</p>
            </div>
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