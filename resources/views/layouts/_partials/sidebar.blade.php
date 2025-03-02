<div class="main-sidebar sidebar-style-2">
    <aside id="sidebar-wrapper">
        <div class="sidebar-brand">
            <a href="#"> <img alt="image" src="assets/img/logo.png" class="header-logo" /> <span
                    class="logo-name">OneLedger</span>
            </a>
        </div>
        <ul class="sidebar-menu">
            <li class="menu-header">Main</li>
            <li class="dropdown {{ request()->is('dashboard') ? 'active' : ''}} ">
                <a href="{{url('/dashboard')}}" class="nav-link"><i data-feather="monitor"></i><span>Dashboard</span></a>
            </li>
            <li class="dropdown {{ request()->is('accounting') ? 'active' : ''}}">
                <a href="#" class="menu-toggle nav-link has-dropdown"><i
                        data-feather="dollar-sign"></i><span>Accounting</span></a>
                <ul class="dropdown-menu">
                    <li><a class="nav-link" href="{{url('/create')}}">Add Transations</a></li>
                    <li><a class="nav-link" href="{{url('/index')}}">Veiw Reports</a></li>
                    <li><a class="nav-link" href="{{url('/report')}}">Audit Trail</a></li>
                </ul>
            </li>
            <li class="dropdown">
                <a href="#" class="menu-toggle nav-link has-dropdown"><i data-feather="credit-card"></i><span>Payroll</span></a>
                <ul class="dropdown-menu">
                    <li><a class="nav-link" href="{{ url('/employee_profiles')}}">Employee Profiles</a></li>
                    <li><a class="nav-link" href="{{url('/salary_processing')}}">Salary Processing</a></li>
                    <li><a class="nav-link" href="{{url('/payroll_reports')}}">Payroll Reports</a></li>
                </ul>
            </li>
            <li class="dropdown">
                <a href="#" class="menu-toggle nav-link has-dropdown"><i data-feather="briefcase"></i><span>Budgeting</span></a>
                <ul class="dropdown-menu">
                    <li><a class="nav-link" href="{{ url('/create_budget')}}">Create Budget </a></li>
                    <li><a class="nav-link" href="{{url('/track_spending')}}">Track Spending</a></li>
                    <li><a class="nav-link" href="{{url('/forecasting')}}">Forecasting</a></li>
                </ul>
            </li>
            <li class="dropdown {{ request()->is('profile') ? 'active' : ''}} ">
                <a href="{{ route('profile.edit') }}" class="nav-link"><i data-feather="user"></i><span>Profile</span></a>
            </li>



        </ul>
    </aside>
</div>
