import { FC, useState, FormEvent, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Login.module.scss';
import { 
  AuthLayout, 
  InputField, 
  Button, 
  EmailIcon, 
  LockIcon,
  EyeIcon,
  EyeOffIcon
} from '../../components';
import { ROUTES } from '../../routes';
import { useAppDispatch, useAppSelector } from '../../redux/hooks';
import { login, clearError } from '../../redux/auth';

// Using Record<string, never> instead of empty interface
type LoginProps = Record<string, never>;

export const Login: FC<LoginProps> = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { loading, error, isAuthenticated } = useAppSelector(state => state.auth);
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<{email?: string; password?: string}>({});

  // If user is already authenticated, redirect to home page
  useEffect(() => {
    if (isAuthenticated) {
      navigate(ROUTES.HOME);
    }
  }, [isAuthenticated, navigate]);

  // Reset server errors when input fields change
  useEffect(() => {
    if (error) {
      dispatch(clearError());
    }
  }, [email, password, dispatch, error]);

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  const validateForm = (): boolean => {
    const newErrors: {email?: string; password?: string} = {};
    
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!password) {
      newErrors.password = 'Password is required';
    }
    
    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    // Send authentication request through Redux
    dispatch(login({ email, password }));
  };

  const goToRegister = () => {
    navigate(ROUTES.REGISTER);
  };

  return (
    <AuthLayout 
      title="Log in to account" 
      subtitle="Enter your credentials to access the service"
    >
      <form className={styles.form} onSubmit={handleSubmit}>
        {error && (
          <div className={styles.serverError}>
            {error}
          </div>
        )}
        
        <InputField
          label="Email"
          icon={<EmailIcon />}
          type="email"
          placeholder="your@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          error={formErrors.email}
        />
        
        <InputField
          label="Password"
          icon={<LockIcon />}
          type={showPassword ? 'text' : 'password'}
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          error={formErrors.password}
          rightIcon={showPassword ? <EyeOffIcon /> : <EyeIcon />}
          onRightIconClick={togglePasswordVisibility}
        />
        
        <div className={styles.forgotPassword}>
          <a href="#" className={styles.link}>Forgot password?</a>
        </div>
        
        <Button
          type="submit"
          disabled={loading}
          className={styles.submitButton}
        >
          {loading ? 'Logging in...' : 'Log in'}
        </Button>
        
        <div className={styles.registerPrompt}>
          <span>Don't have an account yet?</span>
          <button 
            type="button" 
            className={styles.registerLink}
            onClick={goToRegister}
          >
            Register
          </button>
        </div>
      </form>
    </AuthLayout>
  );
}; 