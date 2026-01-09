# Contributing to AWS EC2 Pricing API

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/aws_calculator.git
   cd aws_calculator
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small

### Testing

Before submitting a PR, please test your changes:

```bash
# Test locally
uvicorn api.index:app --reload

# Test endpoints
curl "http://localhost:8000/get-price?instance_type=t3.micro&region=us-east-1"
```

### Commit Messages

Use clear, descriptive commit messages:

- `feat: Add new endpoint for instance comparison`
- `fix: Correct vCPU field name in API response`
- `docs: Update README with new examples`
- `refactor: Improve error handling`

## 🔄 Pull Request Process

1. **Update documentation** if you're adding new features
2. **Test your changes** thoroughly
3. **Ensure code follows** the project's style guidelines
4. **Update CHANGELOG.md** if applicable
5. **Submit PR** with a clear description

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests pass
- [ ] No breaking changes
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

- **Description** of the bug
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment** (Python version, OS, etc.)
- **Error messages** or logs

## 💡 Feature Requests

For feature requests, please:

- Describe the feature clearly
- Explain the use case
- Provide examples if possible
- Consider implementation complexity

## 📚 Documentation

- Update README.md for user-facing changes
- Update API_DOCUMENTATION.md for API changes
- Add code comments for complex logic

## ✅ Code Review

All submissions require review. Please:

- Address review comments promptly
- Be open to feedback
- Keep discussions constructive

## 🙏 Thank You!

Your contributions make this project better for everyone!

