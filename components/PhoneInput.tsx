import React, { useState, useEffect } from 'react';
import { COUNTRY_PHONE_CODES, CountryPhone } from '../constants';

interface PhoneInputProps {
  label: string;
  value: string; // The fully formatted value passed from parent
  onChange: (data: { formatted: string; raw: string; countryCode: string; isValid: boolean }) => void;
  required?: boolean;
  initialCountryCode?: string;
  initialRawValue?: string;
  variant?: 'light' | 'dark'; // Theme support
}

const PhoneInput: React.FC<PhoneInputProps> = ({ 
  label, 
  value, 
  onChange, 
  required = false,
  initialCountryCode = 'TR',
  initialRawValue = '',
  variant = 'light'
}) => {
  const [selectedCountry, setSelectedCountry] = useState<CountryPhone>(
    COUNTRY_PHONE_CODES.find(c => c.code === initialCountryCode) || COUNTRY_PHONE_CODES[0]
  );
  
  // Local state for the raw digits entered by user (without dial code)
  const [rawInput, setRawInput] = useState(initialRawValue);

  // Sync internal state when parent props change (e.g. loading a different profile)
  useEffect(() => {
    if (initialRawValue !== undefined) {
      setRawInput(initialRawValue);
    }
    if (initialCountryCode) {
      const country = COUNTRY_PHONE_CODES.find(c => c.code === initialCountryCode);
      if (country) setSelectedCountry(country);
    }
  }, [initialRawValue, initialCountryCode]);

  useEffect(() => {
    // If parent passes a completely different value structure or reset happens
    if (!value && !initialRawValue) {
        setRawInput('');
    }
  }, [value, initialRawValue]);

  // Format the raw input based on the selected country mask
  const formatNumber = (raw: string, country: CountryPhone) => {
    let i = 0;
    const mask = country.mask;
    let formatted = '';
    
    for (const char of mask) {
      if (i >= raw.length) break;
      if (char === '#') {
        formatted += raw[i];
        i++;
      } else {
        formatted += char;
      }
    }
    return formatted;
  };

  const handleCountryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newCountry = COUNTRY_PHONE_CODES.find(c => c.code === e.target.value);
    if (newCountry) {
      setSelectedCountry(newCountry);
      // Re-trigger change with new country structure but same raw numbers
      triggerChange(rawInput, newCountry);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Extract only digits
    const input = e.target.value;
    
    // We need to strip the prefix and formatting to get raw digits
    const onlyDigits = input.replace(/\D/g, '');
    
    // If the mask limits length, enforce it.
    const maxDigits = selectedCountry.mask.split('#').length - 1;
    const limitedDigits = onlyDigits.slice(0, maxDigits);

    setRawInput(limitedDigits);
    triggerChange(limitedDigits, selectedCountry);
  };

  const triggerChange = (raw: string, country: CountryPhone) => {
    const formattedPart = formatNumber(raw, country);
    const fullFormatted = `${country.dialCode} ${formattedPart}`;
    
    // Calculate validity based on mask length
    const requiredLength = country.mask.split('#').length - 1;
    const isValid = raw.length === requiredLength;

    onChange({
      formatted: fullFormatted,
      raw: raw,
      countryCode: country.code,
      isValid
    });
  };

  const formattedDisplay = formatNumber(rawInput, selectedCountry);

  // Style configurations based on variant
  const isDark = variant === 'dark';
  
  const containerClasses = isDark 
    ? "bg-black/20 text-white border-gray-700 focus:ring-blue-500/30" 
    : "bg-white text-black border-gray-300 focus:ring-blue-500/30";
    
  const labelClasses = isDark ? "text-gray-400" : "text-gray-300 font-semibold";
  const dialCodeColor = isDark ? "text-gray-400" : "text-gray-500";
  const placeholderColor = isDark ? "placeholder-gray-600" : "placeholder-gray-400";
  const arrowColor = isDark ? "text-gray-400" : "text-gray-700";

  // Height adjustment: 'dark' variant usually used in tighter forms (p-2), 'light' in spacious forms (p-3)
  const paddingClass = isDark ? "py-2" : "py-3";

  return (
    <div>
      <label className={`block text-sm mb-1 ${labelClasses}`}>
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <div className="flex gap-2">
        <div className="relative">
          <select
            value={selectedCountry.code}
            onChange={handleCountryChange}
            className={`h-full appearance-none border rounded pl-3 pr-8 focus:outline-none focus:ring-4 focus:border-brand-blue cursor-pointer text-xl transition-colors ${containerClasses}`}
          >
            {COUNTRY_PHONE_CODES.map(c => (
              <option key={c.code} value={c.code} className="text-black text-base">
                {c.flag}
              </option>
            ))}
          </select>
          {/* Custom Arrow */}
          <div className={`pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 ${arrowColor}`}>
            <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
          </div>
        </div>

        <div className="relative w-full">
            <span className={`absolute left-3 top-1/2 -translate-y-1/2 font-medium select-none ${dialCodeColor}`}>
                {selectedCountry.dialCode}
            </span>
            <input
                type="text"
                value={formattedDisplay}
                onChange={handleInputChange}
                className={`w-full border rounded pl-14 pr-3 focus:ring-4 focus:border-brand-blue focus:outline-none transition-all font-mono text-base shadow-sm ${containerClasses} ${paddingClass} ${placeholderColor}`}
                placeholder={selectedCountry.mask.replace(/#/g, '_')}
            />
        </div>
      </div>
    </div>
  );
};

export default PhoneInput;