import { z } from 'zod'

export const loginSchema = z.object({
  email:    z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

export const registerSchema = z.object({
  name:     z.string().min(2, 'Name must be at least 2 characters').max(100),
  email:    z.string().email('Enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .max(100)
    .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Must contain at least one lowercase letter')
    .regex(/\d/, 'Must contain at least one number'),
  role:     z.enum(['CLIENT', 'EXPERT']),
  headline: z.string().max(120).optional(),
  terms:    z.literal(true, { errorMap: () => ({ message: 'You must accept the terms' }) }),
})

export const forgotPasswordSchema = z.object({
  email: z.string().email('Enter a valid email address'),
})

export const resetPasswordSchema = z
  .object({
    token:           z.string().min(1),
    password:        z.string().min(8, 'Password must be at least 8 characters').max(100),
    confirmPassword: z.string(),
  })
  .refine(data => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

export type LoginInput           = z.infer<typeof loginSchema>
export type RegisterInput        = z.infer<typeof registerSchema>
export type ForgotPasswordInput  = z.infer<typeof forgotPasswordSchema>
export type ResetPasswordInput   = z.infer<typeof resetPasswordSchema>
