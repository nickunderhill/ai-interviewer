/**
 * Date Range Filter component for session filtering.
 */
interface DateRangeFilterProps {
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  onClear: () => void;
  onPresetSelect: (days: number) => void;
}

export function DateRangeFilter({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onClear,
  onPresetSelect,
}: DateRangeFilterProps) {
  const presets = [
    { label: 'Last 7 days', days: 7 },
    { label: 'Last 30 days', days: 30 },
    { label: 'Last 3 months', days: 90 },
  ];

  // Check if current date range matches a preset
  const isPresetActive = (days: number) => {
    if (!startDate || !endDate) return false;
    const today = new Date();
    const presetStart = new Date();
    presetStart.setDate(today.getDate() - days);

    return (
      startDate === presetStart.toISOString().split('T')[0] &&
      endDate === today.toISOString().split('T')[0]
    );
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">
          Filter by Date Range
        </h3>
        {(startDate || endDate) && (
          <button
            onClick={onClear}
            className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
          >
            Clear
          </button>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        {presets.map(preset => (
          <button
            key={preset.days}
            onClick={() => onPresetSelect(preset.days)}
            className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
              isPresetActive(preset.days)
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'border-gray-300 hover:bg-gray-50'
            }`}
          >
            {preset.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label
            htmlFor="start-date"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            From
          </label>
          <input
            type="date"
            id="start-date"
            value={startDate}
            onChange={e => onStartDateChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label
            htmlFor="end-date"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            To
          </label>
          <input
            type="date"
            id="end-date"
            value={endDate}
            onChange={e => onEndDateChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>
    </div>
  );
}

export default DateRangeFilter;
