# Contributing to TrueMesh Provider Intelligence

Thank you for your interest in contributing to TrueMesh! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- **Bug Reports**: Report bugs via GitHub Issues
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Improve documentation, examples, or tutorials
- **Testing**: Help with testing and quality assurance

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/TrueMesh.git
   cd TrueMesh
   ```

2. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Services**
   ```bash
   docker-compose up -d postgres redis
   ```

5. **Run Application**
   ```bash
   python main.py
   ```

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for all public functions and classes
- Keep functions focused and concise
- Use meaningful variable and function names

### Code Structure

- **Agents**: Place agent implementations in `app/agents/`
- **API Endpoints**: Place endpoints in `app/api/endpoints/`
- **Models**: Database models go in `app/models/`
- **Core**: Core utilities in `app/core/`

### Agent Development

When creating a new agent:

1. Inherit from `BaseAgent`
2. Implement `get_agent_type()` method
3. Implement `process_task()` method
4. Register in `app/agents/registry.py`
5. Add comprehensive docstrings
6. Include error handling

Example:
```python
from app.core.agent_base import BaseAgent, AgentTask, AgentResult

class MyAgent(BaseAgent):
    """My custom agent description"""
    
    def get_agent_type(self) -> str:
        return "my_agent"
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        # Implementation
        pass
```

### API Development

When adding new endpoints:

1. Create endpoint file in `app/api/endpoints/`
2. Use FastAPI router
3. Add request/response models with Pydantic
4. Include error handling
5. Add docstrings
6. Register router in `app/api/main.py`

### Database Changes

For database schema changes:

```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Review migration file
# Edit if necessary

# Apply migration
alembic upgrade head
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_agents.py
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test names
- Include unit tests and integration tests
- Mock external dependencies

## 📋 Pull Request Process

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

   Use conventional commit messages:
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation changes
   - `test:` test additions/changes
   - `refactor:` code refactoring
   - `chore:` maintenance tasks

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

5. **PR Requirements**
   - Clear description of changes
   - Tests pass
   - Code follows style guidelines
   - Documentation updated
   - No merge conflicts

## 🐛 Bug Reports

When reporting bugs, include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages
- Screenshots if applicable

## 💡 Feature Requests

For feature requests, include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Impact on existing functionality

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on what is best for the community
- Show empathy towards others

## 📞 Questions?

- Open a GitHub Issue for questions
- Tag with `question` label
- We'll respond as soon as possible

Thank you for contributing to TrueMesh! 🎉
