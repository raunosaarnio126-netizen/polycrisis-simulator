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
import { AlertTriangle, Brain, Globe, Shield, TrendingUp, Users, Plus, Play, Eye, MessageSquare, BookOpen, CheckSquare, Target, FileText, Download } from 'lucide-react';

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
            <Dashboard />
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