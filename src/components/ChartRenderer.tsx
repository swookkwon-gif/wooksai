"use client";

import React from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function ChartRenderer({ dataStr }: { dataStr: string }) {
  try {
    const parsedData = JSON.parse(dataStr);
    const { chartType, data, dataKeys, xAxisKey, colors } = parsedData;

    const actualColors = colors || COLORS;

    if (chartType === 'line') {
      return (
        <div className="w-full h-80 my-8 not-prose border border-gray-100 rounded-xl p-4 bg-white shadow-sm">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
              <XAxis dataKey={xAxisKey || 'name'} tick={{ fontSize: 12, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }} />
              {dataKeys.map((key: string, index: number) => (
                <Line 
                  key={key} 
                  type="monotone" 
                  dataKey={key} 
                  stroke={actualColors[index % actualColors.length]} 
                  strokeWidth={3}
                  activeDot={{ r: 6 }}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      );
    }

    if (chartType === 'bar') {
      return (
        <div className="w-full h-80 my-8 not-prose border border-gray-100 rounded-xl p-4 bg-white shadow-sm">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
              <XAxis dataKey={xAxisKey || 'name'} tick={{ fontSize: 12, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <Tooltip 
                cursor={{ fill: '#f3f4f6' }}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }} />
              {dataKeys.map((key: string, index: number) => (
                <Bar 
                  key={key} 
                  dataKey={key} 
                  fill={actualColors[index % actualColors.length]} 
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    }

    return <div className="p-4 bg-red-50 text-red-500 rounded text-sm">Unsupported chart type: {chartType}</div>;
  } catch (e) {
    return <div className="p-4 bg-red-50 text-red-500 rounded text-sm">Invalid chart data JSON format</div>;
  }
}
