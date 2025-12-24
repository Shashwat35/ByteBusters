import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { 
  Search, MapPin, Users, Clock, LogOut, 
  Monitor, Mic, LayoutGrid, Zap, ChevronDown,
  Building, Filter, X, ExternalLink
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const FACILITY_ICONS = {
  'Projector': Monitor,
  'Speaker': Mic,
  'Whiteboard': LayoutGrid,
  'Blackboard': LayoutGrid,
  'Podium': Zap,
};

const FLOORS = ['All Floors', 'Ground', 'First', 'Second'];

export default function DashboardPage() {
  const { user, logout, getAuthHeader } = useAuth();
  const [query, setQuery] = useState('');
  const [rooms, setRooms] = useState([]);
  const [allRooms, setAllRooms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [clarification, setClarification] = useState('');
  const [selectedFloor, setSelectedFloor] = useState('All Floors');
  const [showFilters, setShowFilters] = useState(false);

  // Load all classrooms on mount
  useEffect(() => {
    const loadClassrooms = async () => {
      try {
        const response = await axios.get(`${API}/classrooms`, getAuthHeader());
        setAllRooms(response.data);
        setRooms(response.data);
      } catch (error) {
        console.error('Failed to load classrooms:', error);
        toast.error('Failed to load classrooms');
      } finally {
        setInitialLoading(false);
      }
    };
    loadClassrooms();
  }, []);

  // Filter rooms by floor
  useEffect(() => {
    if (selectedFloor === 'All Floors') {
      setRooms(allRooms);
    } else {
      setRooms(allRooms.filter(room => room.floor === selectedFloor));
    }
  }, [selectedFloor, allRooms]);

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) {
      setRooms(allRooms);
      setMessage('');
      setClarification('');
      return;
    }

    setLoading(true);
    setMessage('');
    setClarification('');

    try {
      const response = await axios.post(
        `${API}/search`,
        { query },
        getAuthHeader()
      );

      if (response.data.message) {
        setMessage(response.data.message);
      }
      if (response.data.clarification_needed) {
        setClarification(response.data.clarification_needed);
      }
      if (response.data.rooms) {
        setRooms(response.data.rooms);
        if (response.data.rooms.length === 0 && !response.data.message) {
          setMessage('No classrooms found matching your criteria.');
        }
      }
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
  };

  const clearSearch = () => {
    setQuery('');
    setRooms(allRooms);
    setMessage('');
    setClarification('');
    setSelectedFloor('All Floors');
  };

  const getPredictionClass = (prediction) => {
    if (prediction === 'Available') return 'prediction-available';
    if (prediction === 'May be occupied') return 'prediction-maybe';
    return 'prediction-after';
  };

  return (
    <div className="min-h-screen dashboard-bg">
      <div className="min-h-screen bg-slate-950/90">
        {/* Header */}
        <header className="border-b border-slate-800/50 backdrop-blur-xl bg-slate-950/50 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-600/20 rounded-lg border border-indigo-500/30">
                  <MapPin className="h-6 w-6 text-indigo-400" />
                </div>
                <div>
                  <h1 className="font-mono text-xl font-bold text-white tracking-tight">IIPS RoomFinder</h1>
                  <p className="text-xs text-slate-500 uppercase tracking-wider">DAVV, Indore</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700/50">
                  <Clock className="h-4 w-4 text-slate-400" />
                  <span className="text-sm text-slate-300">8:00 AM - 6:30 PM</span>
                </div>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button 
                      variant="ghost" 
                      data-testid="user-menu-button"
                      className="flex items-center gap-2 text-slate-300 hover:text-white hover:bg-slate-800"
                    >
                      <div className="w-8 h-8 rounded-full bg-indigo-600/30 border border-indigo-500/50 flex items-center justify-center">
                        <span className="text-sm font-medium text-indigo-300">{user?.name?.charAt(0).toUpperCase()}</span>
                      </div>
                      <span className="hidden md:inline">{user?.name}</span>
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-slate-900 border-slate-700 min-w-[200px]">
                    <div className="px-3 py-2">
                      <p className="text-sm text-white font-medium">{user?.name}</p>
                      <p className="text-xs text-slate-400">{user?.email}</p>
                      <Badge className="mt-2 bg-indigo-600/20 text-indigo-300 border-indigo-500/30 uppercase text-xs">
                        {user?.role}
                      </Badge>
                    </div>
                    <DropdownMenuSeparator className="bg-slate-700" />
                    <DropdownMenuItem 
                      onClick={handleLogout}
                      data-testid="logout-button"
                      className="text-slate-300 hover:text-white hover:bg-slate-800 cursor-pointer"
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      Sign Out
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-8 md:py-12">
          {/* Search Section */}
          <motion.div 
            className="mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-center mb-8">
              <h2 className="font-mono text-3xl md:text-4xl font-bold text-white tracking-tight mb-3">
                Find Your Space
              </h2>
              <p className="text-slate-400 max-w-lg mx-auto">
                Search using natural language like "rooms with projector on ground floor" or "classrooms free at 2 PM"
              </p>
            </div>

            <form onSubmit={handleSearch} className="max-w-3xl mx-auto">
              <div className="relative omnibox rounded-full bg-slate-900/50 border border-slate-700 shadow-2xl">
                <Search className="absolute left-6 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <Input
                  type="text"
                  data-testid="search-input"
                  placeholder="Try: 'Show rooms free on first floor with projector for 60 students'"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="h-14 pl-14 pr-32 text-lg bg-transparent border-0 text-white placeholder:text-slate-500 focus:ring-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                />
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
                  {query && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={clearSearch}
                      data-testid="clear-search-button"
                      className="text-slate-400 hover:text-white"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                  <Button
                    type="submit"
                    data-testid="search-submit-button"
                    disabled={loading}
                    className="h-10 px-6 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                    ) : (
                      'Search'
                    )}
                  </Button>
                </div>
              </div>
            </form>

            {/* Quick Filters */}
            <div className="flex flex-wrap items-center justify-center gap-3 mt-6">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
                data-testid="toggle-filters-button"
                className={`text-slate-400 hover:text-white ${showFilters ? 'bg-slate-800' : ''}`}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </Button>
              
              <AnimatePresence>
                {showFilters && (
                  <motion.div 
                    className="flex flex-wrap gap-2"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                  >
                    {FLOORS.map((floor) => (
                      <Button
                        key={floor}
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedFloor(floor)}
                        data-testid={`floor-filter-${floor.toLowerCase().replace(' ', '-')}`}
                        className={`
                          ${selectedFloor === floor 
                            ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/30' 
                            : 'text-slate-400 hover:text-white hover:bg-slate-800'
                          }
                          border border-slate-700
                        `}
                      >
                        <Building className="h-4 w-4 mr-1" />
                        {floor}
                      </Button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>

          {/* Messages */}
          <AnimatePresence>
            {message && (
              <motion.div 
                className="mb-8 p-4 bg-slate-800/50 border border-slate-700 rounded-xl text-center"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                <p className="text-slate-300" data-testid="search-message">{message}</p>
              </motion.div>
            )}
            
            {clarification && (
              <motion.div 
                className="mb-8 p-4 bg-amber-950/30 border border-amber-900/50 rounded-xl text-center"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                <p className="text-amber-300" data-testid="clarification-message">{clarification}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Results Count */}
          {!initialLoading && (
            <div className="mb-6 flex items-center justify-between">
              <p className="text-slate-400 text-sm">
                Showing <span className="text-white font-medium">{rooms.length}</span> classrooms
                {selectedFloor !== 'All Floors' && ` on ${selectedFloor} Floor`}
              </p>
            </div>
          )}

          {/* Room Grid */}
          {initialLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="skeleton h-64 rounded-xl" />
              ))}
            </div>
          ) : (
            <motion.div 
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <AnimatePresence mode="popLayout">
                {rooms.map((room, index) => (
                  <motion.div
                    key={room.room_id}
                    data-testid={`room-card-${room.room_id}`}
                    className="room-card group relative overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50 p-6 h-full"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    layout
                  >
                    {/* Status Indicator */}
                    <div className="absolute top-4 right-4 flex items-center gap-2">
                      <span className={`status-dot ${room.status === 'Available' ? 'status-available' : 'status-occupied'}`} />
                      <span className={`text-xs font-medium ${room.status === 'Available' ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {room.status}
                      </span>
                    </div>

                    {/* Room ID */}
                    <h3 className="font-mono text-2xl font-bold text-white tracking-tight mb-1">
                      {room.room_id}
                    </h3>
                    
                    {/* Floor */}
                    <p className="text-slate-500 text-sm uppercase tracking-wider mb-4">
                      {room.floor} Floor
                    </p>

                    {/* Capacity */}
                    <div className="flex items-center gap-2 mb-4">
                      <Users className="h-4 w-4 text-slate-400" />
                      <span className="text-slate-300">{room.capacity} seats</span>
                    </div>

                    {/* Facilities */}
                    <div className="flex flex-wrap gap-2 mb-5">
                      {room.facilities.map((facility) => {
                        const Icon = FACILITY_ICONS[facility] || Zap;
                        return (
                          <Badge 
                            key={facility}
                            className="facility-badge bg-slate-800/50 border-slate-700 text-slate-400 text-xs"
                          >
                            <Icon className="h-3 w-3 mr-1" />
                            {facility}
                          </Badge>
                        );
                      })}
                    </div>

                    {/* Predicted Availability */}
                    <div className="border-t border-slate-800 pt-4 mt-auto">
                      <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Predicted Availability</p>
                      <div className="flex gap-2">
                        {Object.entries(room.predicted_availability).map(([key, value]) => (
                          <Badge 
                            key={key}
                            className={`text-xs border ${getPredictionClass(value)}`}
                          >
                            {key.replace('next', '')}m: {value.replace('May be occupied', 'Maybe')}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Map Link */}
                    <a
                      href={room.map_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      data-testid={`map-link-${room.room_id}`}
                      className="absolute bottom-4 right-4 p-2 text-slate-500 hover:text-indigo-400 transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
          )}

          {/* No Results */}
          {!initialLoading && rooms.length === 0 && !message && (
            <motion.div 
              className="text-center py-16"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-slate-800/50 flex items-center justify-center">
                <Search className="h-10 w-10 text-slate-600" />
              </div>
              <h3 className="font-mono text-xl text-white mb-2">No classrooms found</h3>
              <p className="text-slate-400">Try adjusting your search criteria or filters</p>
            </motion.div>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-800/50 mt-16">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <p className="text-center text-slate-500 text-sm">
              IIPS RoomFinder · DAVV, Indore · Campus Hours: 8:00 AM - 6:30 PM
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
