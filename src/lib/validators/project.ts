import { z } from 'zod'

export const createProjectSchema = z.object({
  title: z
    .string()
    .min(10, 'Title must be at least 10 characters')
    .max(120, 'Title must be under 120 characters'),
  description: z
    .string()
    .min(50, 'Please provide more detail (min 50 characters)')
    .max(5000),
  budget: z
    .number({ required_error: 'Budget is required' })
    .min(50, 'Minimum budget is $50')
    .max(1000000),
  budgetType: z.enum(['FIXED', 'HOURLY']),
  timeline: z.number().min(1).max(365).optional(),
  skillIds: z
    .array(z.string())
    .min(1, 'Select at least one required skill')
    .max(10, 'Maximum 10 skills'),
  visibility: z.enum(['PUBLIC', 'INVITE_ONLY']).default('PUBLIC'),
})

export const milestoneSchema = z.object({
  title:       z.string().min(3).max(120),
  description: z.string().min(10).max(1000),
  amount:      z.number().min(10),
  dueDate:     z.string().optional(),
})

export const contractSchema = z.object({
  projectId:  z.string().cuid(),
  expertId:   z.string().cuid(),
  title:      z.string().min(5).max(200),
  terms:      z.string().min(50).max(10000),
  totalValue: z.number().min(50),
  milestones: z.array(milestoneSchema).min(1, 'At least one milestone required'),
})

export const applicationSchema = z.object({
  coverLetter:  z.string().min(100, 'Cover letter must be at least 100 characters').max(2000),
  proposedRate: z.number().min(10).max(10000).optional(),
})

export type CreateProjectInput = z.infer<typeof createProjectSchema>
export type MilestoneInput     = z.infer<typeof milestoneSchema>
export type ContractInput      = z.infer<typeof contractSchema>
export type ApplicationInput   = z.infer<typeof applicationSchema>
