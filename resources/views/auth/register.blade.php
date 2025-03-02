@extends('layouts.auth')

@section('authContent')

    <section class="section">
        <div class="container mt-5">
            <div class="row">
                <div class="col-12 col-sm-10 offset-sm-1 col-md-8 offset-md-2 col-lg-8 offset-lg-2 col-xl-8 offset-xl-2">
                    <div class="card card-primary">
                        <div class="card-header">
                            <h4>Register</h4>
                        </div>
                        <div class="card-body">
                            <form method="POST" action="{{ route('register') }}">
                            @csrf
                                <div class="form-group">
                                    <label for="name">Full Name</label>
                                    <input id="name" type="name" class="form-control" value="{{old('name')}}"  name="name" required>
                                    <div class="invalid-feedback">
                                    </div>
                                    @error('name')
                                    <span>{{ $message }}</span>
                                    @enderror
                                </div>
                                <div class="row">
                                    <div class="form-group col-6">
                                        <label for="business_name">Business Name</label>
                                        <input id="business_name" type="text" class="form-control" value="{{old('business_name')}}" name="business_name" required>
                                        @error('business_name')
                                        <span>{{ $message }}</span>
                                        @enderror
                                    </div>
                                    <div class="form-group col-6">
                                        <label for="email">Email</label>
                                        <input id="email" type="email" class="form-control" value="{{old('email')}}"  name="email" required>
                                        <div class="invalid-feedback">
                                        </div>
                                        @error('email')
                                        <span>{{ $message }}</span>
                                        @enderror
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="form-group col-6">
                                        <label for="password" class="d-block">Password</label>
                                        <input id="password" type="password" class="form-control pwstrength" data-indicator="pwindicator" name="password" required>
                                        <div id="pwindicator" class="pwindicator">
                                            <div class="bar"></div>
                                            <div class="label"></div>
                                        </div>
                                        @error('password')
                                        <span>{{ $message }}</span>
                                        @enderror
                                    </div>
                                    <div class="form-group col-6">
                                        <label for="password_confirmation" class="d-block">Password Confirmation</label>
                                        <input id="password_confirmation" type="password" class="form-control" name="password_confirmation" required>
                                        @error('password_confirmation')
                                        <span>{{ $message }}</span>
                                        @enderror
                                    </div>
                                </div>
                                <div class="form-group">
                                    <div class="custom-control custom-checkbox">
                                        <input type="checkbox" name="agree" class="custom-control-input" id="agree">
                                        <label class="custom-control-label" for="agree">I agree with the terms and conditions</label>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <button type="submit" class="btn btn-primary btn-lg btn-block">
                                        Register
                                    </button>
                                </div>
                            </form>
                        </div>
                        <div class="mb-4 text-muted text-center">
                            Already Registered? <a href="{{url('/login')}}">Login</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

@endsection
