﻿﻿# 🎯 Quick Reference - Admin Dashboard

## Access Points

### Routes
- Dashboard: `http://localhost:5173/admin`
- Tenants: `http://localhost:5173/admin/tenants`
- Users: `http://localhost:5173/admin/users`
- API Keys: `http://localhost:5173/admin/api-keys`
- Contacts: `http://localhost:5173/admin/contacts`
- Campaigns: `http://localhost:5173/admin/campaigns`
- Orders: `http://localhost:5173/admin/orders`
- Invoices: `http://localhost:5173/admin/invoices`
- Analytics: `http://localhost:5173/admin/analytics`

---

## Component Usage

### Button
```jsx
<Button variant="primary" size="md" onClick={handleClick}>
  + Create
</Button>
```
Variants: `primary`, `secondary`, `danger`, `success`, `outline`
Sizes: `sm`, `md`, `lg`

### Card
```jsx
<Card title="Title" className="custom-class">
  Content here
</Card>
```

### Modal
```jsx
<Modal isOpen={show} onClose={() => setShow(false)} title="Modal Title">
  Content here
</Modal>
```

### Table
```jsx
<Table
  headers={['Col1', 'Col2']}
  rows={data}
  actions={(row) => <Button>Edit</Button>}
/>
```

### Input
```jsx
<Input
  label="Email"
  type="email"
  value={value}
  onChange={(e) => setValue(e.target.value)}
  error={errorMessage}
  required
/>
```

### Select
```jsx
<Select
  label="Option"
  value={selected}
  onChange={(e) => setSelected(e.target.value)}
  options={[
    { label: 'Option 1', value: 'opt1' },
    { label: 'Option 2', value: 'opt2' }
  ]}
/>
```

### Badge
```jsx
<Badge variant="green">Active</Badge>
```
Variants: `blue`, `green`, `red`, `yellow`, `gray`

---

## API Methods

### Tenants
```javascript
adminAPI.tenants.create(data)
adminAPI.tenants.getAll()
adminAPI.tenants.getById(id)
adminAPI.tenants.update(id, data)
adminAPI.tenants.delete(id)
```

### Users
```javascript
adminAPI.tenantUsers.getAll(tenantId)
adminAPI.tenantUsers.add(tenantId, data)
adminAPI.tenantUsers.updateRole(tenantId, userId, data)
adminAPI.tenantUsers.remove(tenantId, userId)
```

### API Keys
```javascript
adminAPI.apiKeys.create(tenantId, data)
adminAPI.apiKeys.getAll(tenantId)
adminAPI.apiKeys.delete(tenantId, keyId)
```

### Billing
```javascript
adminAPI.billing.getStats(tenantId)
adminAPI.billing.getInvoices()
adminAPI.billing.createInvoice(data)
adminAPI.billing.updateInvoice(id, data)
adminAPI.billing.createReminder(invoiceId, data)
```

### Orders
```javascript
adminAPI.orders.create(data)
adminAPI.orders.getAll()
adminAPI.orders.getById(id)
adminAPI.orders.update(id, data)
adminAPI.orders.markPacked(orderId, itemId)
```

### Campaigns
```javascript
adminAPI.campaigns.createStep(campaignId, data)
adminAPI.campaigns.getSteps(campaignId)
adminAPI.campaigns.enrollContact(contactId, campaignId)
adminAPI.campaigns.getProgress(contactId, campaignId)
```

---

## Tailwind Classes Quick Reference

### Spacing
- `p-4` = padding: 1rem
- `m-6` = margin: 1.5rem
- `gap-4` = gap: 1rem

### Colors
- `text-gray-900` = Dark text
- `text-gray-600` = Medium text
- `bg-blue-600` = Blue background
- `border-gray-300` = Gray border

### Sizing
- `w-full` = width: 100%
- `h-screen` = height: 100vh
- `max-w-2xl` = max-width: 42rem

### Display
- `flex` = display: flex
- `grid` = display: grid
- `hidden` = display: none
- `block` = display: block

### Responsive
- `md:` = @media (min-width: 768px)
- `lg:` = @media (min-width: 1024px)

---

## State Management

### Auth Context
```jsx
const { user, isAdmin, login, logout } = useAuth()
```

### Tenant Context
```jsx
const { currentTenant, tenants, switchTenant, createTenant } = useTenant()
```

---

## Common Patterns

### Form Handling
```jsx
const [formData, setFormData] = useState({ name: '', email: '' })
const [error, setError] = useState(null)

const handleSubmit = async (e) => {
  e.preventDefault()
  try {
    await adminAPI.operation(formData)
    // Success
  } catch (err) {
    setError(err.message)
  }
}
```

### Data Loading
```jsx
const [data, setData] = useState([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState(null)

useEffect(() => {
  loadData()
}, [dependency])

const loadData = async () => {
  try {
    const response = await adminAPI.method()
    setData(response.data || response)
  } catch (err) {
    setError(err.message)
  } finally {
    setLoading(false)
  }
}
```

### Modal Management
```jsx
const [showModal, setShowModal] = useState(false)

<Button onClick={() => setShowModal(true)}>Open</Button>

<Modal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  title="Title"
>
  Content
</Modal>
```

---

## File Locations

### Pages
- `src/pages/AdminDashboard.jsx`
- `src/pages/TenantsPage.jsx`
- `src/pages/UsersPage.jsx`
- `src/pages/APIKeysPage.jsx`
- `src/pages/ContactsPage.jsx`
- `src/pages/CampaignsPage.jsx`
- `src/pages/OrdersPage.jsx`
- `src/pages/InvoicesPage.jsx`
- `src/pages/AnalyticsPage.jsx`

### Components
- `src/components/AdminLayout.jsx` - Main layout
- `src/components/UI.jsx` - All UI components

### Contexts
- `src/contexts/AuthContext.jsx` - Authentication
- `src/contexts/TenantContext.jsx` - Tenant management

### Services
- `src/services/api.js` - API client

---

## Environment Variables

```
VITE_API_URL=http://localhost:8000
```

---

## Installation & Setup

```bash
# Install dependencies
cd apps/ui
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Debugging Tips

1. **Check Console:** Open browser DevTools → Console
2. **Network Tab:** Monitor API calls
3. **React DevTools:** Inspect component tree
4. **LocalStorage:** Check auth tokens and tenant ID
5. **API Response:** Verify backend is running

---

## Common Issues & Solutions

### "API is not responding"
- Check backend is running on correct port
- Verify VITE_API_URL environment variable
- Check browser network tab for 404/500 errors

### "Tenant context is undefined"
- Ensure TenantProvider wraps routes in App.jsx
- Check that AuthProvider is parent of TenantProvider

### "Styling looks broken"
- Run `npm install` to ensure Tailwind is installed
- Clear browser cache (Ctrl+Shift+Delete)
- Check tailwind.config.js is present

### "Modal not showing"
- Verify `isOpen` state is toggled correctly
- Check Modal component is rendered
- Inspect browser console for errors

---

## Performance Tips

1. **Memoization:** Use React.memo for expensive components
2. **Lazy Loading:** Use React.lazy for code splitting
3. **Debounce:** Debounce search inputs
4. **Pagination:** Paginate large tables
5. **Caching:** Cache API responses

---

## Security Reminders

✅ Keep API tokens in localStorage (session lifecycle)
✅ Never expose API keys in client code
✅ Validate all inputs before submission
✅ Confirm before delete operations
✅ Use HTTPS in production
✅ Set secure cookie flags

---

## Deployment Checklist

- [ ] Run `npm run build`
- [ ] Test production build with `npm run preview`
- [ ] Set VITE_API_URL to production backend
- [ ] Configure environment variables
- [ ] Setup CI/CD pipeline
- [ ] Configure SSL/TLS
- [ ] Setup monitoring
- [ ] Test all features
- [ ] Performance test
- [ ] Security audit

---

## Resources

- **React Docs:** https://react.dev
- **Tailwind CSS:** https://tailwindcss.com
- **Axios Docs:** https://axios-http.com
- **React Router:** https://reactrouter.com
- **Vite:** https://vitejs.dev

---

## Support

For issues:
1. Check documentation files
2. Review component source code
3. Check browser console
4. Inspect network requests
5. Verify backend is running

---

**Last Updated:** January 14, 2026
**Version:** Phase 3 Complete
**Status:** Production Ready ✅

